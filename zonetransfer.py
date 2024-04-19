#!/usr/bin/env python

import argparse
import dns.query
import dns.resolver
import dns.zone
import csv

def get_ns(zone):
    """Returns the nameservers associated with the domain provided as an 
    argument.
    
    Arguments:
        zone (string): Domain to be analysed.
    """
    try:
        name_servers = dns.resolver.resolve(zone, 'NS')
    except Exception as e:
        print(e)
        return None
    else:
        for server in name_servers:
            print(f"[*] Found NS: {server}")
        return name_servers

def get_zone(ip,domain):
    """ Try a zone transfer using the ip of the name server and the domain to 
        be analysed.
        Return the zone or None if the server doesn't allow zone transfer.
    
    Arguments:
        ip (dns.rdtypes.IN.A.A): IP address of the authoritative server for 
            the zone.
        domain (string): Domain to be analysed.    
    """
    try:
        zone = dns.zone.from_xfr(dns.query.xfr(str(ip),domain))
    except Exception:
        print(f"    The IP {ip} doesn't allow zone transfer")
        return None
    else:
        print(f"    The IP {ip} allow zone transfer")
        return zone

def extract_records(zone):
    """ Returns a list of the A and CNAME records of the dns zone to be sent to 
    the corresponding output.
    
    Arguments:
        zone (dns.zone.Zone): Object Zone with the records returned by the 
            analyzed zone.
    """
    records = []
    for name, node in zone.nodes.items():
        for rdataset in node.rdatasets:
            if rdataset.rdtype in [dns.rdatatype.A, dns.rdatatype.CNAME]:
                for rdata in rdataset:
                    records.append((str(name), rdata.to_text()))
    return records

def zone_to_csv(data,domain):
    """ Writes a CSV file with the name of the zone containing the zone records.
    
    Arguments:
        data (list): Records of the dns zone.
        domain (string): Domain to be analysed.
    """
    csv_file_path = domain + '.csv'
    with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Subdomain', 'IP'])
            for record in data:
                writer.writerow(record)
    print("File " + domain + ".csv writed")

def zone_to_stdout(data):
    """ Outputs the records of the zone to stdout.
    
    Arguments:
        data (list): Records of the dns zone.
    """
    print()
    print("{: >20} {: >20}".format('Subdomain', 'IP'))
    for row in data:
        print("{: >20} {: >20}".format(*row))

def sort_ip(data):
    """ Sorts the records in the dns zone by IP and returns a dictionary using 
    the IP address as a key and a list of subdomains as a value.
    
    Arguments:
        data (list): Records of the dns zone.
    """
    ordered = {}
    for subdomain, ip in data:
        if ip not in ordered:
            ordered[ip] = []
        ordered[ip].append(subdomain)

    return ordered

def zone_to_graph(data, domain):
    """ Writes an HTML file using the cytoscape library to display the zone 
    records as a graph.
    
    Arguments:
        data (list): Records of the dns zone.
        domain (string): Domain to be analysed.
    """
    ips = sort_ip(data)
    with open( domain + '.html', 'w') as f:
        f.write('<html>\n<head>\n<title>Graph with Cytoscape</title>\n')
        f.write('<script ' + 
                'src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/' + 
                '3.20.1/cytoscape.min.js">' +
                '</script>\n')

        f.write('<style>#cy {width: 1920px; height: 1080px; display: block;}' +
                '</style>')

        f.write('</head>\n<body>\n')
        f.write('<div id="cy"></div>\n')
        
        # Open script tag
        f.write('<script>\n')
        f.write('var cy = cytoscape({\n')
        f.write('container: document.getElementById(\'cy\'),\n')
        
        # Write data in elements
        f.write('elements: [\n')

        edge = 0
        for ip in ips:
            f.write('{data: ' +
                    '{{ id: \'{0}\', label: \'{0}\' }} }},\n'.format(ip))    
            for subdomain in ips[ip]:
                f.write('{data: ' +
                        '{{ id: \'{0}\', label: \'{0}\' }} }},\n'
                        .format(subdomain))
                edge = edge + 1
                f.write('{data: ' +
                        '{{id: \'{}\', source: \'{}\', target: \'{}\'}}}},\n'
                        .format(edge, subdomain, ip))
                        
        f.write('],\n')

        # Write layout
        f.write('layout: { name: \'concentric\' },\n')

        # Write style
        f.write(' style: [{ selector: \'node\', ' +
                ' style: { shape: \'round-tag\',' +
                ' \'background-color\': \'blue\', ' +
                ' label: \'data(id)\'} }] ')
        f.write('});\n')

        # Close script tag
        f.write('</script>\n')
        
        f.write('</body>\n</html>\n')

    print("File " + domain + ".html writed")

def main():
    parser = argparse.ArgumentParser(prog='zonetransfer',
                                    description="Test DNS Zone Transfer")
    parser.add_argument('domain', 
                            type=str, 
                            help='Domain to test the zone transfer')
    parser.add_argument('--output-format',
                            '-f', choices=['csv', 'stdout', 'graph'], 
                            default='stdout',
                            help='Output format (csv, stdout, html)')

    args = parser.parse_args()
    name_servers = get_ns(args.domain)
    if name_servers is not None:
        for server in name_servers:
            addr = dns.resolver.resolve(server.target, 'A')
            ip = addr.rrset[0]
            print(f"[*] Found A: {ip} ({server})")
            zone = get_zone(ip,args.domain)
            if zone is not None:
                data = extract_records(zone)
                if args.output_format == 'csv':
                    zone_to_csv(data,args.domain)
                elif args.output_format == 'stdout':
                    zone_to_stdout(data)
                elif args.output_format == 'graph':
                    zone_to_graph(data,args.domain)
                break

if __name__ == "__main__":
    main()
