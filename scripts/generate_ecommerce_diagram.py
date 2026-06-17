import os
# Ensure Windows can find the Graphviz executable
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import Fastapi
from diagrams.onprem.database import Postgresql
from diagrams.aws.ml import Sagemaker

# The graph_attr dict sets the resolution to 300 DPI for Ultra HD quality
graph_attr = {
    "dpi": "300",
    "pad": "0.5"
}

with Diagram("E-Commerce Product Page Architecture", show=False, filename="ecommerce_architecture", outformat="png", graph_attr=graph_attr):
    
    client = Users("Product Page (Client)")
    gateway = Nginx("API Gateway")

    client >> gateway

    with Cluster("Microservices Layer"):
        auth_api = Fastapi("Auth API")
        item_api = Fastapi("Item API")
        reviews_api = Fastapi("Reviews API")
        search_api = Fastapi("Search API")
        rec_api = Fastapi("Recommendations API")

    with Cluster("Data Isolation Layer (Database-per-Service)"):
        auth_db = Postgresql("Auth DB")
        item_db = Postgresql("Item DB")
        reviews_db = Postgresql("Reviews DB")
        search_db = Postgresql("Search DB")
        rec_db = Postgresql("Recommendations DB")
        
    with Cluster("Artificial Intelligence"):
        ai_model = Sagemaker("Recommendation\nML Model")

    # Connect Gateway to all APIs
    gateway >> Edge(color="darkgreen", style="solid") >> auth_api
    gateway >> Edge(color="darkgreen", style="solid") >> item_api
    gateway >> Edge(color="darkgreen", style="solid") >> reviews_api
    gateway >> Edge(color="darkgreen", style="solid") >> search_api
    gateway >> Edge(color="darkgreen", style="solid") >> rec_api

    # Connect APIs to their isolated databases
    auth_api >> auth_db
    item_api >> item_db
    reviews_api >> reviews_db
    search_api >> search_db
    rec_api >> rec_db

    # Cross-Service Dependencies (as specified in your requirements)
    reviews_api >> Edge(label="fetch item details", style="dashed", color="darkred") >> item_api
    search_api >> Edge(label="index item data", style="dashed", color="darkred") >> item_api
    rec_api >> Edge(label="fetch item metrics", style="dashed", color="darkred") >> item_api
    rec_api >> Edge(label="fetch search context", style="dashed", color="darkblue") >> search_api
    
    # AI Integration
    rec_api >> Edge(label="infer", style="dotted", color="purple") >> ai_model