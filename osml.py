from utils.overpass_client import OverpassClient

ql_text = '(node(51.249,7.148,51.251,7.152);<;)'

overpass_client = OverpassClient()
result = overpass_client.query(ql_text=ql_text)
print 'Done'
