# import sparql
#
# endpoint = "http://localhost:3030/netflix"
# s = sparql.Service(endpoint)
# statement = "select * where{Graph <http://iiitd.ac.in/sweb/your-rollno/oldmoviesgraph>{?s ?p ?o.}}"
# result = s.query(statement)
# for row in result.fetchone():
#     print(row)

import sparql

endpoint = "http://localhost:3030/netflix"
query = "Prefix title: <http://example.com/> SELECT Distinct ?MOVIE ?Genre WHERE {GRAPH <http://iiitd.ac.in/sweb/your-rollno/oldmoviesgraph> { ?MOVIE title:@1 ?Genre Filter (regex(?Genre,@2)) } }"

var1 = "isOfGenre"
var2 = "\'Comed\'"
var3 = "'Action'"

pq = sparql.prepare_query(query)
pq.set_variable(2,var2)
pq.set_variable(1,var1)


result = sparql.my_own(endpoint, pq,method="GET")
for row in result.fetchone():
    print(row)
    