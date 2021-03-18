from solrcloudpy import *
from solrcloudpy.collection import schema
conn=SolrConnection(['dats.swordfishsecurity.ru:8983'])
print(conn.list())

test_data=["""
{
  "id" : 587605975,
  "content_t" : "I said this early, and I don’t know why it got lost.\r\nRather than adding more arguments, let’s just modify the job after `newJob` for the tests that need it. Honestly, I should have done the same for completion mode.",
  "origin_url_s" : "https://github.com/kubernetes/kubernetes/pull/98727#discussion_r587605975",
  "content_created_dt" : "2021-03-04T16:13:14Z",
  "content_modified_dt" : "2021-03-04T16:14:30Z",
  "source_attributes" : {
    "author_association_s" : "MEMBER",
    "user" : {
      "login_s" : "alculquicondor",
      "type_s" : "User",
      "html_url_s" : "https://github.com/alculquicondor",
      "site_admin_b" : false
    }
  },
  "author_ident_s" : "alculquicondor",
  "kind_s" : "comment",
  "context_dpath" : "Kubernetes/pr-review/comment",
  "context_apath" : "Kubernetes/pr-review/comment",
  "reference_s" : "0c8233b3b7068e0b3bddc470d5b5f83c",
  "source_s" : "github"
}
"""]

test_data=["""
{
  "id" : 587605975,
  "content_t" : "I said this early, and I don’t know why it got lost.\r\nRather than adding more arguments, let’s just modify the job after `newJob` for the tests that need it. Honestly, I should have done the same for completion mode.",
  "origin_url_s" : "https://github.com/kubernetes/kubernetes/pull/98727#discussion_r587605975",
  "content_created_dt" : "2021-03-04T16:13:14Z",
  "content_modified_dt" : "2021-03-04T16:14:30Z",
  "author_ident_s" : "alculquicondor",
  "kind_s" : "comment",
  "context_dpath" : "Kubernetes/pr-review/comment",
  "context_apath" : "Kubernetes/pr-review/comment",
  "reference_s" : "0c8233b3b7068e0b3bddc470d5b5f83c",
  "source_s" : "github"
}
"""]

# test1=conn['test1'].create(collection_config_name='venafi_configset')
# print(conn['test1'].add(test_data))
# test1.commit()

# conn['test1'].drop()

commentsScheme = schema.SolrSchema(conn,'test1')
# syn_data={'test':['assert|1.0']}
# print(commentsScheme.add_synonym(syn_data))
print(commentsScheme.delete_synonym("test"))