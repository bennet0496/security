import math
import sys
import urllib3
import io
import ipaddress
import certifi
from packaging import version
import datetime

RIR_TABLES = {
    "APNIC": "https://ftp.apnic.net/stats/apnic/delegated-apnic-latest",
    "AFRINIC": "https://ftp.afrinic.net/stats/afrinic/delegated-afrinic-latest",
    "ARIN": "https://ftp.arin.net/pub/stats/arin/delegated-arin-extended-latest",
    "LACNIC": "https://ftp.lacnic.net/pub/stats/lacnic/delegated-lacnic-latest",
    "RIPE": "https://ftp.ripe.net/ripe/stats/delegated-ripencc-extended-latest"
}

ISO_RIR = {
    "AF": "APNIC",      "AX": "RIPE",       "AL": "RIPE",       "DZ": "AFRINIC",    "AS": "APNIC",      "AD": "RIPE",
    "AO": "AFRINIC",    "AI": "ARIN",       "AQ": "ARIN",       "AG": "ARIN",       "AR": "LACNIC",     "AM": "RIPE",
    "AW": "LACNIC",     "AU": "APNIC",      "AT": "RIPE",       "AZ": "RIPE",       "BS": "ARIN",       "BH": "RIPE",
    "BD": "APNIC",      "BB": "ARIN",       "BY": "RIPE",       "BE": "RIPE",       "BZ": "LACNIC",     "BJ": "AFRINIC",
    "BM": "ARIN",       "BT": "APNIC",      "BO": "LACNIC",     "BA": "AFRINIC",    "BW": "AFRINIC",    "BV": "ARIN",
    "BR": "LACNIC",     "IO": "APNIC",      "BN": "APNIC",      "BG": "RIPE",       "BF": "AFRINIC",    "BI": "AFRINIC",
    "KH": "APNIC",      "CM": "AFRINIC",    "CA": "ARIN",       "CV": "AFRINIC",    "KY": "ARIN",       "CF": "AFRINIC",
    "TD": "AFRINIC",    "CL": "LACNIC",     "CN": "APNIC",      "CX": "APNIC",      "CC": "APNIC",      "CO": "LACNIC",
    "KM": "AFRINIC",    "CG": "AFRINIC",    "CD": "AFRINIC",    "CK": "APNIC",      "CR": "LACNIC",     "CI": "AFRINIC",
    "HR": "RIPE",       "CU": "LACNIC",     "CY": "RIPE",       "CZ": "RIPE",       "DK": "RIPE",       "DJ": "AFRINIC",
    "DM": "ARIN",       "DO": "LACNIC",     "EC": "LACNIC",     "EG": "AFRINIC",    "SV": "LACNIC",     "GQ": "AFRINIC",
    "ER": "AFRINIC",    "EE": "RIPE",       "ET": "AFRINIC",    "FK": "LACNIC",     "FO": "RIPE",       "FJ": "APNIC",
    "FI": "RIPE",       "FR": "RIPE",       "GF": "LACNIC",     "PF": "APNIC",      "TF": "APNIC",      "GA": "AFRINIC",
    "GM": "AFRINIC",    "GE": "RIPE",       "DE": "RIPE",       "GH": "AFRINIC",    "GI": "RIPE",       "GR": "RIPE",
    "GL": "RIPE",       "GD": "ARIN",       "GP": "ARIN",       "GU": "APNIC",      "GT": "LACNIC",     "GG": "RIPE",
    "GN": "AFRINIC",    "GW": "AFRINIC",    "GY": "LACNIC",     "HT": "LACNIC",     "HM": "ARIN",       "VA": "RIPE",
    "HN": "LACNIC",     "HK": "APNIC",      "HU": "RIPE",       "IS": "RIPE",       "IN": "APNIC",      "ID": "APNIC",
    "IR": "RIPE",       "IQ": "RIPE",       "IE": "RIPE",       "IM": "RIPE",       "IL": "RIPE",       "IT": "RIPE",
    "JM": "ARIN",       "JP": "APNIC",      "JE": "RIPE",       "JO": "RIPE",       "KZ": "RIPE",       "KE": "AFRINIC",
    "KI": "APNIC",      "KP": "APNIC",      "KR": "APNIC",      "KW": "RIPE",       "KG": "RIPE",       "LA": "APNIC",
    "LV": "RIPE",       "LB": "RIPE",       "LS": "AFRINIC",    "LR": "AFRINIC",    "LY": "AFRINIC",    "LI": "RIPE",
    "LT": "RIPE",       "LU": "RIPE",       "MO": "APNIC",      "MK": "RIPE",       "MG": "AFRINIC",    "MW": "AFRINIC",
    "MY": "APNIC",      "MV": "APNIC",      "ML": "AFRINIC",    "MT": "RIPE",       "MH": "APNIC",      "MQ": "ARIN",
    "MR": "AFRINIC",    "MU": "AFRINIC",    "YT": "AFRINIC",    "MX": "LACNIC",     "FM": "APNIC",      "MD": "RIPE",
    "MC": "RIPE",       "MN": "APNIC",      "ME": "RIPE",       "MS": "RIPE",       "MA": "AFRINIC",    "MZ": "AFRINIC",
    "MM": "APNIC",      "NA": "AFRINIC",    "NR": "APNIC",      "NP": "APNIC",      "NL": "RIPE",       "AN": "LACNIC",
    "NC": "APNIC",      "NZ": "APNIC",      "NI": "LACNIC",     "NE": "AFRINIC",    "NG": "AFRINIC",    "NU": "APNIC",
    "NF": "APNIC",      "MP": "APNIC",      "NO": "RIPE",       "OM": "RIPE",       "PK": "APNIC",      "PW": "APNIC",
    "PS": "RIPE",       "PA": "LACNIC",     "PG": "APNIC",      "PY": "LACNIC",     "PE": "LACNIC",     "PH": "APNIC",
    "PN": "APNIC",      "PL": "RIPE",       "PT": "RIPE",       "PR": "ARIN",       "QA": "RIPE",       "RE": "AFRINIC",
    "RO": "RIPE",       "RU": "RIPE",       "RW": "AFRINIC",    "KN": "ARIN",       "SH": "ARIN",       "LC": "ARIN",
    "MF": "ARIN",       "PM": "ARIN",       "VC": "ARIN",       "WS": "APNIC",      "SM": "RIPE",       "ST": "AFRINIC",
    "SA": "RIPE",       "SN": "AFRINIC",    "RS": "RIPE",       "SC": "AFRINIC",    "SL": "AFRINIC",    "SG": "APNIC",
    "SK": "RIPE",       "SI": "RIPE",       "SB": "APNIC",      "SO": "AFRINIC",    "ZA": "AFRINIC",    "GS": "LACNIC",
    "ES": "RIPE",       "LK": "APNIC",      "SD": "AFRINIC",    "SR": "ARIN",       "SJ": "RIPE",       "SZ": "AFRINIC",
    "SE": "RIPE",       "CH": "RIPE",       "SY": "RIPE",       "TW": "APNIC",      "TJ": "RIPE",       "TZ": "AFRINIC",
    "TH": "APNIC",      "TL": "APNIC",      "TG": "AFRINIC",    "TK": "APNIC",      "TO": "APNIC",      "TT": "LACNIC",
    "TN": "AFRINIC",    "TR": "RIPE",       "TM": "RIPE",       "TC": "ARIN",       "TV": "APNIC",      "UG": "AFRINIC",
    "UA": "RIPE",       "AE": "RIPE",       "GB": "RIPE",       "US": "ARIN",       "UM": "ARIN",       "UY": "LACNIC",
    "UZ": "RIPE",       "VU": "APNIC",      "VE": "LACNIC",     "VN": "APNIC",      "VG": "ARIN",       "VI": "ARIN",
    "WF": "APNIC",      "EH": "AFRINIC",    "YE": "RIPE",       "ZM": "AFRINIC",    "ZW": "AFRINIC",
}

ISO_COUNTRY = {
    "AF": "AFGHANISTAN",                                  "AX": "ALAND ISLANDS",                          "AL": "ALBANIA",
    "DZ": "ALGERIA",                                      "AS": "AMERICAN SAMOA",                         "AD": "ANDORRA",
    "AO": "ANGOLA",                                       "AI": "ANGUILLA",                               "AQ": "ANTARCTICA",
    "AG": "ANTIGUA & BARBUDA",                            "AR": "ARGENTINA",                              "AM": "ARMENIA",
    "AW": "ARUBA",                                        "AU": "AUSTRALIA",                              "AT": "AUSTRIA",
    "AZ": "AZERBAIJAN",                                   "BS": "BAHAMAS",                                "BH": "BAHRAIN",
    "BD": "BANGLADESH",                                   "BB": "BARBADOS",                               "BY": "BELARUS",
    "BE": "BELGIUM",                                      "BZ": "BELIZE",                                 "BJ": "BENIN",
    "BM": "BERMUDA",                                      "BT": "BHUTAN",                                 "BO": "BOLIVIA",
    "BA": "BOSNIA & HERZEGOVINA",                         "BW": "BOTSWANA",                               "BV": "BOUVET ISLAND",
    "BR": "BRAZIL",                                       "IO": "BRITISH INDIAN OCEAN TERRITORY",         "BN": "BRUNEI DARUSSALAM",
    "BG": "BULGARIA",                                     "BF": "BURKINA FASO",                           "BI": "BURUNDI",
    "KH": "CAMBODIA",                                     "CM": "CAMEROON",                               "CA": "CANADA",
    "CV": "CAPE VERDE",                                   "KY": "CAYMAN ISLANDS",                         "CF": "CENTRAL AFRICAN REPUBLIC",
    "TD": "CHAD",                                         "CL": "CHILE",                                  "CN": "CHINA",
    "CX": "CHRISTMAS ISLAND",                             "CC": "COCOS (KEELING) ISLANDS",                "CO": "COLOMBIA",
    "KM": "COMOROS",                                      "CG": "CONGO",                                  "CD": "CONGO, DEMOCRATIC REPUBLIC OF THE",
    "CK": "COOK ISLANDS",                                 "CR": "COSTA RICA",                             "CI": "COTE D’IVOIRE",
    "HR": "CROATIA (Hrvatska)",                           "CU": "CUBA",                                   "CY": "CYPRUS",
    "CZ": "CZECH REPUBLIC",                               "DK": "DENMARK",                                "DJ": "DJIBOUTI",
    "DM": "DOMINICA",                                     "DO": "DOMINICAN REPUBLIC",                     "EC": "ECUADOR",
    "EG": "EGYPT",                                        "SV": "EL SALVADOR",                            "GQ": "EQUATORIAL GUINEA",
    "ER": "ERITREA",                                      "EE": "ESTONIA",                                "ET": "ETHIOPIA",
    "FK": "FALKLAND ISLANDS (MALVINAS)",                  "FO": "FAROE ISLANDS",                          "FJ": "FIJI",
    "FI": "FINLAND",                                      "FR": "FRANCE",                                 "GF": "FRENCH GUIANA",
    "PF": "FRENCH POLYNESIA",                             "TF": "FRENCH SOUTHERN TERRITORIES",            "GA": "GABON",
    "GM": "GAMBIA",                                       "GE": "GEORGIA",                                "DE": "GERMANY",
    "GH": "GHANA",                                        "GI": "GIBRALTAR",                              "GR": "GREECE",
    "GL": "GREENLAND",                                    "GD": "GRENADA",                                "GP": "GUADELOUPE",
    "GU": "GUAM",                                         "GT": "GUATEMALA",                              "GG": "GUERNSEY",
    "GN": "GUINEA",                                       "GW": "GUINEA-BISSAU",                          "GY": "GUYANA",
    "HT": "HAITI",                                        "HM": "HEARD & MC DONALD ISLANDS",              "VA": "HOLY SEE (VATICAN CITY STATE)",
    "HN": "HONDURAS",                                     "HK": "HONG KONG",                              "HU": "HUNGARY",
    "IS": "ICELAND",                                      "IN": "INDIA",                                  "ID": "INDONESIA",
    "IR": "IRAN (ISLAMIC REPUBLIC OF)",                   "IQ": "IRAQ",                                   "IE": "IRELAND",
    "IM": "ISLE OF MAN",                                  "IL": "ISRAEL",                                 "IT": "ITALY",
    "JM": "JAMAICA",                                      "JP": "JAPAN",                                  "JE": "JERSEY",
    "JO": "JORDAN",                                       "KZ": "KAZAKHSTAN",                             "KE": "KENYA",
    "KI": "KIRIBATI",                                     "KP": "KOREA, DEMOCRATIC PEOPLE’S REPUBLIC OF", "KR": "KOREA, REPUBLIC OF",
    "KW": "KUWAIT",                                       "KG": "KYRGYZSTAN",                             "LA": "LAO PEOPLE’S DEMOCRATIC REPUBLIC",
    "LV": "LATVIA",                                       "LB": "LEBANON",                                "LS": "LESOTHO",
    "LR": "LIBERIA",                                      "LY": "LIBYAN ARAB JAMAHIRIYA",                 "LI": "LIECHTENSTEIN",
    "LT": "LITHUANIA",                                    "LU": "LUXEMBOURG",                             "MO": "MACAU",
    "MK": "MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF",   "MG":  "MADAGASCAR",                            "MW": "MALAWI",
    "MY": "MALAYSIA",                                     "MV": "MALDIVES",                               "ML": "MALI",
    "MT": "MALTA",                                        "MH": "MARSHALL ISLANDS",                       "MQ": "MARTINIQUE",
    "MR": "MAURITANIA",                                   "MU": "MAURITIUS",                              "YT": "MAYOTTE",
    "MX": "MEXICO",                                       "FM": "MICRONESIA, FEDERATED STATES OF",        "MD": "MOLDOVA, REPUBLIC OF",
    "MC": "MONACO",                                       "MN": "MONGOLIA",                               "ME": "MONTENEGRO",
    "MS": "MONTSERRAT",                                   "MA": "MOROCCO",                                "MZ": "MOZAMBIQUE",
    "MM": "MYANMAR",                                      "NA": "NAMIBIA",                                "NR": "NAURU",
    "NP": "NEPAL",                                        "NL": "NETHERLANDS",                            "AN": "NETHERLANDS ANTILLES",
    "NC": "NEW CALEDONIA",                                "NZ": "NEW ZEALAND",                            "NI": "NICARAGUA",
    "NE": "NIGER",                                        "NG": "NIGERIA",                                "NU": "NIUE",
    "NF": "NORFOLK ISLAND",                               "MP": "NORTHERN MARIANA ISLANDS",               "NO": "NORWAY",
    "OM": "OMAN",                                         "PK": "PAKISTAN",                               "PW": "PALAU",
    "PS": "PALESTINIAN TERRITORY",                        "PA": "PANAMA",                                 "PG": "PAPUA NEW GUINEA",
    "PY": "PARAGUAY",                                     "PE": "PERU",                                   "PH": "PHILIPPINES",
    "PN": "PITCAIRN",                                     "PL": "POLAND",                                 "PT": "PORTUGAL",
    "PR": "PUERTO RICO",                                  "QA": "QATAR",                                  "RE": "REUNION",
    "RO": "ROMANIA",                                      "RU": "RUSSIAN FEDERATION",                     "RW": "RWANDA",
    "KN": "SAINT KITTS & NEVIS",                          "SH": "ST. HELENA",                             "LC": "SAINT LUCIA",
    "MF": "SAINT MARTIN",                                 "PM": "ST. PIERRE & MIQUELON",                  "VC": "SAINT VINCENT & THE GRENADINES",
    "WS": "SAMOA",                                        "SM": "SAN MARINO",                             "ST": "SAO TOME & PRINCIPE",
    "SA": "SAUDI ARABIA",                                 "SN": "SENEGAL",                                "RS": "SERBIA",
    "SC": "SEYCHELLES",                                   "SL": "SIERRA LEONE",                           "SG": "SINGAPORE",
    "SK": "SLOVAKIA (Slovak Republic)",                   "SI": "SLOVENIA",                               "SB": "SOLOMON ISLANDS",
    "SO": "SOMALIA",                                      "ZA": "SOUTH AFRICA",                           "GS": "SOUTH GEORGIA & THE SOUTH SANDWICH ISLANDS",
    "ES": "SPAIN",                                        "LK": "SRI LANKA",                              "SD": "SUDAN",
    "SR": "SURINAME",                                     "SJ": "SVALBARD & JAN MAYEN ISLANDS",           "SZ": "SWAZILAND",
    "SE": "SWEDEN",                                       "CH": "SWITZERLAND",                            "SY": "SYRIAN ARAB REPUBLIC",
    "TW": "TAIWAN",                                       "TJ": "TAJIKISTAN",                             "TZ": "TANZANIA, UNITED REPUBLIC OF",
    "TH": "THAILAND",                                     "TL": "TIMOR-LESTE",                            "TG": "TOGO",
    "TK": "TOKELAU",                                      "TO": "TONGA",                                  "TT": "TRINIDAD & TOBAGO",
    "TN": "TUNISIA",                                      "TR": "TURKEY",                                 "TM": "TURKMENISTAN",
    "TC": "TURKS & CAICOS ISLANDS",                       "TV": "TUVALU",                                 "UG": "UGANDA",
    "UA": "UKRAINE",                                      "AE": "UNITED ARAB EMIRATES",                   "GB": "UNITED KINGDOM",
    "US": "UNITED STATES",                                "UM": "UNITED STATES MINOR OUTLYING ISLANDS",   "UY": "URUGUAY",
    "UZ": "UZBEKISTAN",                                   "VU": "VANUATU",                                "VE": "VENEZUELA, BOLIVARIAN REPUBLIC OF",
    "VN": "VIET NAM",                                     "VG": "VIRGIN ISLANDS (BRITISH)",               "VI": "VIRGIN ISLANDS (U.S.)",
    "WF": "WALLIS & FUTUNA ISLANDS",                      "EH": "WESTERN SAHARA",                         "YE": "YEMEN",
    "ZM": "ZAMBIA",                                       "ZW": "ZIMBABWE",
}

CACHE = {
    "APNIC": [],
    "AFRINIC": [],
    "ARIN": [],
    "LACNIC": [],
    "RIPE": []
}

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def download_list(rir):
    if rir not in RIR_TABLES.keys():
        print("# Unknown RIR {}".format(rir))
        return None

    if len(CACHE[rir]) > 0:
        print("# Reusing RIR CACHE for {}".format(ISO_RIR[cc]))
        rir_list = CACHE[rir]
    else:
        print("# Downloading RIR from {}".format(rir))
        http = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        )
        r = http.request('GET', RIR_TABLES[rir], preload_content=False)
        if version.parse(urllib3.__version__) < version.parse("1.25"):
            class ExplicitlyClosedHttpResponse(urllib3.HTTPResponse):
                @property
                def closed(self):
                    return self._fp.closed
            # change the class from standard urllib3.HttpResponse
            r.__class__ = ExplicitlyClosedHttpResponse
        else:
            r.auto_close = False

        rir_raw = [line.strip('\n').split("|") for line in io.TextIOWrapper(r) if not line.startswith("#")]
        rir_header = rir_raw[:4]
        rir_list = rir_raw[4:]

        del rir_raw

        rversion,registry,_,records,startdate,enddate,_  = rir_header[0]
        
        try:
            startdate = datetime.datetime.strptime(startdate, '%Y%m%d').strftime('%a %b %d %Y')
        except ValueError:
            startdate = "N/A"
        try:
            enddate = datetime.datetime.strptime(enddate, '%Y%m%d').strftime('%a %b %d %Y')
        except ValueError:
            enddate = "N/A"

        print("# Got {}/{} v{} allocations from {}".format(len(rir_list), records, rversion, str(registry).upper()))
        print("# {} - {}".format(startdate, enddate))
        print("# {}:{} {}:{} {}:{}".format(rir_header[1][2], rir_header[1][4],rir_header[2][2], rir_header[2][4], rir_header[3][2], rir_header[3][4]))
        CACHE[rir] = rir_list
    
    return rir_list

    

def filter(cc, net):
    rir = ISO_RIR[cc]
    if len(CACHE[rir]) == 0:
        download_list(rir)

    print("# Filtering for {}".format(ISO_COUNTRY[cc]))
    if net == "all":
        filtered_list = [n for n in CACHE[rir] if n[1].upper() == cc.upper() and n[2].lower() != "asn"]
    else:
        filtered_list = [n for n in CACHE[rir] if n[1].upper() == cc.upper() and n[2].lower() == net.lower()]

    print("# Got {} allocations from {} for {}".format(len(filtered_list), rir, ISO_COUNTRY[cc]))

    return filtered_list


def generate_range(cc, net, quiet = False):
    rir_list = filter(cc, net)
    return_list = []
    # 0: registry
    # 1: cc
    # 2: type
    # 3: start -> ipv4: count of hosts, ipv6: CIDR prefix length
    # 4: value
    # 5: date
    # 6: status
    for entry in rir_list:
        # calculate the inital assumed network mask from the number of hosts
        if entry[2] == "ipv4":
            cidr_mask_inital = int(32 - math.log2(int(entry[4])))
        else:
            cidr_mask_inital = int(entry[4])

        cidr_mask = cidr_mask_inital

        shrink = True
        # the network may not correspond with the calculated CIDR mask
        # leading to cases where the network address has hostbits set
        # i.e. the start address would be in the middle of the network
        # in this case we need to shrink the network into smaller subnets
        while shrink:
            if cidr_mask > 128:
                # implausible
                raise Exception("Giving Up!")
            try:
                network = ipaddress.ip_network("{}/{}".format(entry[3], cidr_mask))
                shrink = False # we are good and dont need to shrink
            except ValueError:
                # Shrink the network and try again
                cidr_mask += 1
                print("# Network duplication glitch {}/{}v{}".format(entry[3], cidr_mask_inital, cidr_mask))

        # print network range if not suppressed
        if not quiet:
            print("{}-{}".format(format(network.network_address), format(network.broadcast_address)))

        # add the working network
        return_list.append(network)

        # if we had to shrink the network add the missing network, after
        # the working one
        if cidr_mask != cidr_mask_inital:
            # broadcast (last address) of the previous network
            previous_broadcast = network.broadcast_address
            for _ in range(cidr_mask - cidr_mask_inital):  # we have (cidr_mask - cidr_mask_inital) networks of size `cidr_mask` to add
                # current network, immediated after the broadcast address of the previous
                current_network = ipaddress.ip_network("{}/{}".format(format(previous_broadcast + 1), cidr_mask))
                return_list.append(current_network)
                # get the current broadcast address for the next itteration
                previous_broadcast = current_network.broadcast_address
                # print network range if not suppressed
                if not quiet:
                    print("{}-{}".format(format(current_network.network_address), format(current_network.broadcast_address)))

    return return_list


def generate_cidr(cc, net):
    for e in generate_range(cc, net, True):
        print(format(e))


def generate_list(cc, net):
    for e in generate_range(cc, net, True):
        for h in list(e.hosts()):
            print(format(h))


if __name__ == '__main__':
    net = "all"
    mode = "cidr"
    sys.argv.pop(0)
    if "-4" in sys.argv:
        sys.argv.remove("-4")
        net = "ipv4"
    if "-6" in sys.argv:
        sys.argv.remove("-6")
        net = "ipv6"
    if "-cidr" in sys.argv:
        sys.argv.remove("-cidr")
        mode = "cidr"
    if "-list" in sys.argv:
        sys.argv.remove("-list")
        mode = "list"
    if "-range" in sys.argv:
        sys.argv.remove("-range")
        mode = "range"

    for cc in sys.argv:
        if cc not in ISO_RIR.keys():
            print("# Ignoring unknown Code: {}".format(cc))
            continue
        if mode == "cidr":
            generate_cidr(cc, net)
        elif mode == "list":
            generate_list(cc, net)
        elif mode == "range":
            generate_range(cc, net)
        else:
            print("# Unkown mode {}".format(mode))
