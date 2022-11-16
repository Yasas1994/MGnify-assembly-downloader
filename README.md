# MGnify-assembly-downloader
Downloads all assemblies available on MGnify. Based on the original script by https://github.com/bastiaanvonmeijenfeldt to download data from MGnify databse using its API



###  Dependencies 

```
pip install jsonapi-client
```
## How to use this tool?

first run get_analyses_and_assemblies.py to get a list of accession numbers of studies with assemblies from MGnify.
by default, these accession numbers are written to "analyses_and_assembly.txt" 
run the second script with the output of the first script. usage of the second script is available below.


```
python get_analyses_and_assemblies.py
python download_assemblies.py -i analyses_and_assembly.txt  -d list_of_integers
```
 option -d of the second script accepts a list of integers. each integer specifies what exactly you want to download from MGnify for the corresponding accession id. for example if you want to download both contigs and predicted ORFS


```
python download_assemblies.py -i analyses_and_assembly.txt  -d 1 3
```

### how to use the second script
```
usage: download_assemblies.py [-h] -i INPUT [-d DOWNLOAD [DOWNLOAD ...]]

MGnify assembly downloader v.1.0

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        list of analyses ids
  -d DOWNLOAD [DOWNLOAD ...], --download DOWNLOAD [DOWNLOAD ...]
                        1: Processed contigs
                        2: Predicted CDS (aa)
                        3: Predicted ORF (nt)
                        4: Diamond annotation
                        5: Complete GO annotation
                        6: GO slim annotation
                        7: InterPro matches
                        8: KEGG orthologues annotation
                        9: Pfam annotation
                        10: Contigs encoding SSU rRNA
                        11: MAPseq SSU assignments
                        12: OTUs, counts and taxonomic assignments for SSU rRNA
                        13: Contigs encoding LSU rRNA
                        14: MAPseq LSU assignments
                        15: OTUs, counts and taxonomic assignments for LSU rRNA
                        17: antiSMASH annotation
                        18: antiSMASH annotation19: Genome Properties annotation
                        20: KEGG pathway annotation
```
