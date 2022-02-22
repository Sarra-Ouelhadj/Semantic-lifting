import pyexcel as p
from unidecode import unidecode
from rdflib import Graph, RDFS, RDF, Literal, URIRef, OWL
from rdflib.namespace import XSD, DCTERMS
import os

def convertToCamelcase(words):
    '''(list) -> string

    Convert a list of strings to a camelCase string.

    >>> convertToCamelcase(["Hello", "World", "Python", "Programming"])
    helloWorldPythonProgramming
    '''
    s = "".join(word[0].upper() + word[1:].lower() for word in words)
    return s[0].lower() + s[1:] 

def convertToPascalcase(words):
    '''(list) -> string

    Convert a list of strings to a PascalCase string.

    >>> convertToPascalcase(["Hello", "World", "Python", "Programming"])
    HelloWorldPythonProgramming
    '''
    return "".join(word[0].upper() + word[1:].lower() for word in words) 

template_GeoJSON = """PREFIX iter: <http://w3id.org/sparql-generate/iter/>
PREFIX fun: <http://w3id.org/sparql-generate/fn/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

GENERATE {{
    ?{generated_class_variable} a <{class_type}> ;
        {body_part1}
    <http://www.opengis.net/ont/geosparql#asWKT> ?geometricCoordinates .
}}
    SOURCE <{dataset_link}> AS ?source
    ITERATOR iter:GeoJSON(?source) AS ?geometricCoordinates ?properties
    
    WHERE {{
        BIND(IRI(CONCAT("{class_instance_base_link}",fun:JSONPath(?properties,"$.{class_instance_identifier}"))) AS ?{generated_class_variable})
        {body_part2}

    }}"""

g = Graph()

#Open the template file
book = p.get_book_dict(file_name="/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/input.ods")

#What do I need to create the SPARQL-Generate request file
dataset_link = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrcomgl&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171"
bind_line="""BIND (fun:JSONPath(?properties,"$.{column_source}") AS ?{column_source})"""
generated_class_variable = book["Classes"][1][0]
class_instance_base_link = "https://data.grandlyon.com/id/commune/"
class_definition=book["Classes"][1][1]
body_part1=""
body_part2=""
class_type = book["Classes"][1][2]

#What do I need to create the ontology file
ontology_namespace = "https://data.grandlyon.com/ontology/"



if class_type=="" :
    class_type = URIRef(ontology_namespace + generated_class_variable)
    
    #ontology classes
    g.add((class_type, RDF.type, OWL.Class))
    g.add((class_type, RDFS.label, Literal(generated_class_variable)))
    g.add((class_type, RDFS.comment,Literal(class_definition)))

for class_attribut_ref_link in book["Attributes"][1:]:
    if class_attribut_ref_link[3]=="": 
        attributeURI=URIRef(class_type+"#"+convertToCamelcase(unidecode(class_attribut_ref_link[1]).split()))
        #ontology data properties
        g.add((attributeURI, RDF.type, OWL.DatatypeProperty))
        g.add((attributeURI, RDFS.label, Literal(class_attribut_ref_link[1])))
        g.add((attributeURI, RDFS.comment, Literal(class_attribut_ref_link[2])))

    body_part1 =body_part1+"<"+class_attribut_ref_link[3] +">"+ " ?" +class_attribut_ref_link[4]+";\n"
    
    #URI minting strategy
    if class_attribut_ref_link[5]=="yes": class_instance_identifier=class_attribut_ref_link[4]
    body_part2=body_part2+bind_line.format(column_source=class_attribut_ref_link[4])+"\n"
        

template_GeoJSON=template_GeoJSON.format(generated_class_variable=generated_class_variable,class_type= class_type,body_part1=body_part1,dataset_link=dataset_link,class_instance_base_link=class_instance_base_link,class_instance_identifier=class_instance_identifier,body_part2=body_part2)        

with open("/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/query_GeoJSON.rq","w") as fichier_out1, open("/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/ontology.ttl","w") as fichier_out2 :
    fichier_out1.write(template_GeoJSON)
    fichier_out2.write(g.serialize(format="turtle"))

#os.system('java -jar /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/sparql-generate-2.0.9.jar --query-file /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/query_GeoJSON.rq --output /home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/test/results.ttl')
