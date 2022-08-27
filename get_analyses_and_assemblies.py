#download a list of accession ids of assembly experiments from MGnfy database
import time
import datetime
import requests
import json
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed



def get_pagination(page_size):
    API_BASE = f'https://www.ebi.ac.uk/metagenomics/api/v1/analyses?page={1}&page_size={page_size}'
    response=requests.get(API_BASE)
    json_obj=json.loads(response.content)
    links = json_obj["meta"]
    return links["pagination"] #{page: int, pages int, count : int}


def get_assembly_and_analyses_ids(page_number):
    out = []
    API_BASE = f'https://www.ebi.ac.uk/metagenomics/api/v1/analyses?page={page_number}&page_size={1000}'
    response=requests.get(API_BASE)

    json_obj=json.loads(response.content)
    time.sleep(0.75)
    
    current = json_obj["meta"]["pagination"]["page"]
    if current // 100 == 0:
        print(f"processing page number {current}")
        
    for analyses in json_obj["data"]:
        analysis_id = analyses["id"] #analysis id
        assembly_id = analyses["relationships"]["assembly"]["data"]
        if assembly_id:
            out.append(f"{analysis_id}, {assembly_id['type']}, {assembly_id['id']}")
    return out

def main():
    date = str(datetime.date.today())
    out_file = f'{date}_analyses_and_assembly.txt'
    pagination = get_pagination(1000)
    MIN_PAGE = pagination["page"]
    MAX_PAGE = pagination["pages"]

    with ThreadPoolExecutor(max_workers=3) as pool, open(out_file, "w") as outf:
        # submit tasks
        futures = [pool.submit(get_assembly_and_analyses_ids, task) for task in range(MIN_PAGE,MAX_PAGE)]
        # get results as they are available
        for future in as_completed(futures):
            # get the result
            result = future.result()
            if result:
                for r in result:
                    outf.write(r+'\n')

if __name__ == '__main__':
    main()
