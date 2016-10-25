#!/usr/bin/env python2

"""
This program converts named zone file (RFC 1035/1034) into
batch job for amazon aws cli to add dns records into route 53.
It splits large files into smaller ones since AWS API has
limit of 1000 records per batch

Basically you use this tool to import DNS zones into route53 with AWS cli tool

Inspired by
https://aws.amazon.com/developertools/Amazon-Route-53/4495891528591897
'BIND to Amazon Route 53 Conversion Tool'
which does pretty much the same thing but result is direct API request payload
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import dns.zone, getopt, sys, json
import dns.rdatatype

__author__ = "Eugene Aleynikov"
__license__ = "GPL"


def usage():
    """Prints usage"""
    print (sys.argv[0], "--name origin --zone zonefile\n")

def main():
    """Code entry point"""
    try:
        opts, dummy_args = getopt.getopt(sys.argv[1:], "hz:n:", ["help", "zone=", "name="])
    except getopt.GetoptError, err:
        print (str(err)) # will print something like "option -a not recognized"
        usage()
        return

    name = None
    zone = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return
        elif o in ("-z", "--zone"):
            zone = a
        elif o in ("-n", "--name"):
            name = a
        else:
            assert False, "unhandled option"

    if not name or not zone:
        usage()
        return

    z = dns.zone.from_file(zone, relativize=False)
    allnames = z.nodes.keys()
    allnames.sort()
    fileno = 0
    batchsize = 900
    for names in [allnames[i:i+batchsize] for i in range(0, len(allnames), batchsize)]:
        fileno = fileno + 1
        out = {"Comment": "Zone file import {} via bind2route53.py".format(fileno),
               "Changes": []}
        for n in names:
            for rdataset in z[n].rdatasets:
                if rdataset.rdtype == dns.rdatatype.SOA:
                    continue

                if rdataset.rdtype == dns.rdatatype.NS:
                    continue

                rr = dict()
                rr['Action'] = 'CREATE'
                rr['ResourceRecordSet'] = dict()
                rr['ResourceRecordSet']['Name'] = n.to_text()
                rr['ResourceRecordSet']['Type'] = dns.rdatatype.to_text(rdataset.rdtype)
                rr['ResourceRecordSet']['TTL'] = rdataset.ttl
                rr['ResourceRecordSet']['ResourceRecords'] = list()
                for rdata in rdataset:
                    rr['ResourceRecordSet']['ResourceRecords'].append({"Value": rdata.to_text()})

                out["Changes"].append(rr)


            #print (z[n].to_text(n))
            #print (n)

        if len(out["Changes"]) > 0:
            filename = "{}-{}.json".format(name, fileno)
            with open(filename, 'w') as wh:
                print ("Writing {}, to import please run:".format(filename))
                json.dump(out, wh)
                print ("aws route53 change-resource-record-sets --hosted-zone-id <ZONEID> --change-batch  file://{}".format(filename))


if __name__ == "__main__":
    main()
#EOF
