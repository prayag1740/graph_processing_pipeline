import pandas
from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()
        self.session = self._driver.session()

    def get_or_create_graph(self, weight_property):
        graph_name = 'trip'
        check_graph_query = 'call gds.graph.list '
        res_check = self.session.run(check_graph_query)
        res_check_val = res_check.values()
        if res_check_val != []:
            print("graph already exists")
            return
        print("creating a new graph")
        self.session.run("CALL gds.graph.project('trip','Location','TRIP',{relationshipProperties : $weight_property, nodeProperties: 'name'})", weight_property=weight_property)
        print("created a new graph trip")
        

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):

        self.get_or_create_graph('weight')

        query = """MATCH (start:Location {name: $start_node})
            MATCH (end:Location {name: $last_node})
            CALL gds.bfs.stream('trip',{
              sourceNode: id(start),
              targetNodes : [id(end)]
            })
            YIELD  path
            RETURN path"""

        
        res = self.session.run(query, start_node=start_node, last_node=last_node)
        res_data = res.data()

        return res_data
        
        

    def pagerank(self, max_iterations, weight_property):

        self.get_or_create_graph(weight_property)
        
        res = self.session.run("""CALL gds.pageRank.stream('trip', 
            { maxIterations: $max_iterations, relationshipWeightProperty: $weight_property})
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).name AS node, score
            ORDER BY score DESC""", max_iterations=max_iterations, weight_property=weight_property)
        res_v = res.values()
        res_array = []
        maxy = {"name" : res_v[0][0], "score" : res_v[0][1]}
        miny = {"name" : res_v[-1][0], "score" : res_v[-1][1]}
        res_array.append(maxy)
        res_array.append(miny)
        return res_array

        


