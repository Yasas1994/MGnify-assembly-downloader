
import enum
import html
import os
import urllib.request
import datetime
import argparse
from argparse import RawTextHelpFormatter
from jsonapi_client import Session
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from concurrent.futures import as_completed
import time 

def arg_parser():
    parser = argparse.ArgumentParser(description="MGnify assembly downloader v.1.0", formatter_class=RawTextHelpFormatter)
    
    parser.add_argument('-i', '--input', required=True, 
        help="list of analyses ids")
    parser.add_argument('-d','--download',nargs='+', type= int,
                        help="1: Processed contigs\n2: Predicted CDS (aa)\n3: Predicted ORF (nt)\n4: Diamond annotation\n5: Complete GO annotation\n6: GO slim annotation\n7: InterPro matches\n"+
                    "8: KEGG orthologues annotation\n9: Pfam annotation\n10: Contigs encoding SSU rRNA\n11: MAPseq SSU assignments\n12: OTUs, counts and taxonomic assignments for SSU rRNA\n"+
                    "13: Contigs encoding LSU rRNA\n14: MAPseq LSU assignments\n15: OTUs, counts and taxonomic assignments for LSU rRNA\n17: antiSMASH annotation\n18: antiSMASH annotation"+
                    "19: Genome Properties annotation\n20: KEGG pathway annotation" )


    args = parser.parse_args()
    return args

def format_unit(unit):
    if unit:
        return html.unescape(unit)
    else:
        return ""
    
    
def convert_metadata(metadata):
    d = {}
    
    for (i, m) in enumerate(metadata):
        d[i] = (m['key'], m['value'], format_unit(m['unit']))
        
    return d



def clean_sample_desc(sample_desc):
    try:
        if '\n' in sample_desc:
            if '\r\n' in sample_desc:
                c = sample_desc.replace('\r\n', ' ')
            else:
                c = sample_desc.replace('\n', ' ')
                
            return ' '.join([w for w in c.split(' ') if w != ''])
        else:
            return sample_desc
    except:
        # Prevent the 'argument of type 'NoneType' is not iterable' error.
        return sample_desc
    
    
def clean_species(species):
    try:
        # Some species have a new line at the beginning.
        return species.lstrip()
    except:
        return species
    
    
#####
# Functions to write individual files.
#####


def write_study_name_and_abstract(study, out_file): #this is cool
    with open(out_file, 'w') as outf:
        outf.write(f'name: {study.study_name}'+'\n')
        outf.write(f'abstract: {study.study_abstract}'+'\n')
        
        
def write_sample_metadata(sample, out_file): # it okay to pass the fname as these are separate files
    with open(out_file, 'w') as outf:
        metadata = convert_metadata(sample.sample_metadata)
        
        for i in sorted(metadata, key=int):
            (key, value, unit) = metadata[i]
            
            outf.write(f'{key}\t{value}\t{unit}\n')
                
            
#####
# Functions to write general files.
#####


def write_studies_file(study=None, studies_fh=None): # again pass the file handle 
    
    studies_fh.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\n'
                    ''.format(study.accession, study.bioproject,
                        study.secondary_accession, study.centre_name,
                        study.data_origination, study.last_update,
                        study.public_release_date, study.samples_count))
                    
                    
def write_samples_file(sample=None, samples_fh=None):

    samples_fh.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}\t{10}'
            '\t{11}\t{12}\t{13}\t{14}\t{15}\n'
            ''.format(sample.accession,
                ';'.join([study.accession for
                    study in sample.studies]),
                sample.sample_name, sample.sample_alias,
                clean_sample_desc(sample.sample_desc),
                sample.biome.lineage, sample.environment_biome,
                sample.environment_feature,
                sample.environment_material, sample.geo_loc_name,
                sample.latitude, sample.longitude,
                sample.analysis_completed, sample.last_update,
                clean_species(sample.species), sample.host_tax_id))
                    
                    
def write_analyses_file(analysis=None, analyses_fh=None):

    analyses_fh.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'
            ''.format(analysis.accession, analysis.assembly.accession,
                analysis.sample.accession, analysis.study.accession,
                analysis.pipeline_version, analysis.complete_time))
            
def download_files(analysis_accession,download_options):
    out_data = {'errors':[], 'analysis':[] , 'sample' :[], 'study': []}

    API_BASE = 'https://www.ebi.ac.uk/metagenomics/api/latest/'
    with Session(API_BASE) as s:
        try: #handles 404 error 
            analysis = s.get('analyses', analysis_accession).resource

            #write_analyses_file(analysis, analyses_fh) #should be removed
            out_data["analysis"].append(analysis)
            os.makedirs(f'analyses_assemblies/{analysis_accession}', exist_ok=True)

            # Download all the user specified files.
            for download in analysis.downloads: 
                if download.description.label in download_options:
                    id_ = download.id
                    url = download.url

                    try:
                        #time.sleep(0.01)
                        urllib.request.urlretrieve(url,
                                'analyses_assemblies/'
                                f'{analysis_accession}/{id_}')


                    except:

                        # Write the analysis accession to the first
                        # error file but add (url) to it, so that it's
                        # clear where it went wrong.
                        out_data['errors'].append(f'{analysis_accession} {url}\n')

            out_data['sample'].append(analysis.sample)
            out_data['study'].append(analysis.study)
        except Exception as e:
            print(e, analysis_accession)
            out_data['errors'].append(f'{e} : {analyses_accession}\n')
    return out_data      

def main():
    options = { 1:'Processed contigs',
                2:'Predicted CDS (aa)',
                3:'Predicted ORF (nt)',
                4:'Diamond annotation',
                5:'Complete GO annotation',
                6:'GO slim annotation',
                7:'InterPro matches',
                8:'KEGG orthologues annotation',
                9:'Pfam annotation',
                10:'Contigs encoding SSU rRNA',
                11:'MAPseq SSU assignments',
                12:'OTUs, counts and taxonomic assignments for SSU rRNA',
                13:'Contigs encoding LSU rRNA',
                14:'MAPseq LSU assignments',
                15:'OTUs, counts and taxonomic assignments for LSU rRNA',
                17:'antiSMASH annotation',
                18:'antiSMASH annotation',
                19:'Genome Properties annotation',
                20:'KEGG pathway annotation' }

    args = arg_parser()
    download_options = set([options[i] for i in  args.download])
    # Make directories.
    os.makedirs('analyses_assemblies', exist_ok=True)
    os.makedirs('studies_name_and_abstract', exist_ok=True)
    os.makedirs('samples_metadata', exist_ok=True)
    os.makedirs('additional', exist_ok=True)
    date = str(datetime.date.today())
    # Construct output files. First numerical in the name reflects the level
    # of hierarchy, 1 being the highest, 4 the lowest. NOTE that there are no
    # runs for assemblies.
    #write_studies_file()
    # write_samples_file()
    # write_analyses_file()
    studies_file = './additional/1_studies.txt'
    samples_file = './additional/2_samples.txt'
    analyses_file = './additional/4_analyses.txt'

    # This error file lists all analyses where something went wrong whilst
    # retrieving information from MGnify, including analyses where something
    # went wrong during the download.
    error_file_1 = f'./additional/not_downloaded.assemblies.{date}_analyses.txt'

    # This error file lists all downloads that did not succeed.
    # error_file_2 = f'./additional/not_downloaded.assemblies.{date}_analyses.urls.txt'

    with open(studies_file, 'w') as studies_fh, open(samples_file, 'w') as samples_fh, \
        open(analyses_file, 'w') as analyses_fh,open(error_file_1, 'w') as errf1:
        #lets write the headers 
        studies_fh.write('study.accession\t'
                    'study.bioproject\t'
                    'study.secondary_accession\t'
                    'study.centre_name\t'
                    'study.data_origination\t'
                    'study.last_update\t'
                    'study.public_release_date\t'
                    'study.samples_count\n')

        samples_fh.write('sample.accession\t'
                    '\';\'.join([study.accession for study in sample.studies])\t'
                    'sample.sample_name\t'
                    'sample.sample_alias\t'
                    'sample.sample_desc\t'
                    'sample.biome.lineage\t'
                    'sample.environment_biome\t'
                    'sample.environment_feature\t'
                    'sample.environment_material\t'
                    'sample.geo_loc_name\t'
                    'sample.latitude\t'
                    'sample.longitude\t'
                    'sample.analysis_completed\t'
                    'sample.last_update\t'
                    'sample.species\t'
                    'sample.host_tax_id\n')
        

        analyses_fh.write('analysis.accession\t'
                'analysis.assembly.accession\t'
                'analysis.sample.accession\t'
                'analysis.study.accession\t'
                'analysis.pipeline_version\t'
                'analysis.complete_time\n')




        studies_trace = set()
        samples_trace = set()

        file_ = args.input

    #analysis_accession = line.split(',')[0] #get the accession number
    with ThreadPoolExecutor(max_workers=3) as pool, open(file_, 'r') as f:
        # submit tasks
        futures = []
        for line_no,line in enumerate(f):
            task = line.split(',')[0]
            futures.append(pool.submit(download_files, task,download_options))
        # get results as they are available
        for future in as_completed(futures):
            # get the result

            out_data = future.result()

            if out_data:

                for study in out_data["study"]:   
                    print(study.accession)
                    if study.accession not in studies_trace:
                        out_file = ('studies_name_and_abstract/'
                                f'{study.accession}.name_and_abstract')
                        write_study_name_and_abstract(study, out_file) #should be removed
                        with open(studies_file, 'a') as studies_fh:
                            write_studies_file(study, studies_fh) #should be removed

                        studies_trace.add(study.accession) #should be removed

                for sample in out_data["sample"]:  

                    if sample.accession not in samples_trace:
                        out_file = ('samples_metadata/'
                                f'{sample.accession}.metadata')
                        write_sample_metadata(sample, out_file) #should be removed
                        open(samples_file, 'a') as samples_fh:
                            write_samples_file(sample, samples_fh) #should be removed

                        samples_trace.add(sample.accession) 

                for analysis in out_data["analysis"]:
                    with open(analyses_file, 'a') as analyses_fh:
                        write_analyses_file(analysis, analyses_fh)

                for errors in out_data["errors"]:
                    with open(error_file_1, 'a') as errf1:
                        errf1.write(errors)
                        

if __name__ == '__main__':
    main()
