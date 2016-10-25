# bind2route53
Tool to import DNS zone into route53 format...

## Usage

- Install dnspython (in Debian do `aptitude install python-dnspython`)
- Obtain zone file
- Run the script `bind2route53.py -z domain.com.zone -n domain.com`

This will produce json batch jobs to feed to aws cli tool via 
`aws route53 change-resource-record-sets --hosted-zone-id <ZONEID> --change-batch  file://domain.com.json`

Note that program automatically strips NS and SOA records because those are provided by route53 itself.
