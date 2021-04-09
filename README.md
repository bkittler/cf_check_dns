## cf_check_dns.py - tool to check cloudflare dns export
***

cf_check_dns.py is python tool to check cloudflare dns export

This tool takes a txt file containing a json export of the dns cloudflare entries as an entry and displays the status of each entry: 
	
* HTTPS / HTTP test with the return code 
	
* ping of the ip

## Installation

Please first clone repository :

    git clone https://github.com/bkittler/cf_check_dns

    cd ./cf_check_dns

And install Python and requirements :

    pip install -r requirements.txt


## Usage

Synthax with display in the console: 

    cf_check_dns.py dns-json.txt

Syntax with output to file:

    cf_check_dns.py dns-json.txt > result.dns-json.txt


dns-json.txt is json export of the dns cloudflare entries. Your file can have another name.


## Output

The tool display output :

Testing : host (domain_identified)  Type A (Entry Type)-> X.X.X.X (IP identified on input file)

Resolution -> ['X.X.X.X', 'X.X.X.X'] (Real resolution of domain identified)

Response code HTTPS : (Response code)

Response ping : (Ping OK or KO)


## Diff

To make diff between two result file, you can make :

    diff -u result1.dns-json.txt result2.dns-json.txt


## Dependencies

please install python dependancies before run tool :

    pip install -r requirements.txt 

## Further information and help

GitHub has an excellent [documentation](https://help.github.com/). Check it out if you need help!

For further questions please contact [Kittler](https://www.kittler.fr/).
 
