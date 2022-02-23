import myLibrary as lib
import os

dataset_link = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrcomgl&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171"
class_instance_base_link = "https://data.grandlyon.com/id/commune/"
file_name="/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/input.ods"
ontology_namespace = "https://data.grandlyon.com/ontology/"
path="/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/test"

lib.createGeoJSONQueryForSPARQLGenerate(dataset_link,class_instance_base_link,file_name, path, ontology_namespace)

#os.system('java -jar /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/sparql-generate-2.0.9.jar --query-file /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/query_GeoJSON.rq --output /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/test/results.ttl')
