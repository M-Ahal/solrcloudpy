from solrcloudpy import *
conn=SolrConnection(['dats.swordfishsecurity.ru:8983'])
print(conn.list())