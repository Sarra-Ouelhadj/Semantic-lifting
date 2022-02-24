import pyexcel as p
from unidecode import unidecode
from rdflib.namespace import XSD, DCTERMS
from rdflib import Graph, RDFS, Literal, RDF, OWL, URIRef

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

def createGeoJSONQueryForSPARQLGenerate(dataset_link, class_instance_base_link, file, result_path, ontology_namespace=None):
    '''
   
    Create a SPARQL-Generate query for GeoJSON data format 

    '''
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
    book = p.get_book_dict(file_name=file)

    #What do I need to create the SPARQL-Generate request file
    bind_line="""BIND (fun:JSONPath(?properties,"$.{column_source}") AS ?{column_source})"""
    body_part1=""
    body_part2=""
    cl = {}

    #Parse Classes sheet -> return a dictionnary of dictionnaries and ontology classes
    for classes in book["Classes"][1:]:
        classe_dic = {
            "class_name" : convertToPascalcase(unidecode(classes[0]).split()), #class name
            "class_URI" : URIRef(classes[2]) if classes[2]!="" else URIRef(ontology_namespace + classes[0]) #class reference link
        } 
        cl[classes[0]]=classe_dic
        
        #ontology classes
        g.add((classe_dic["class_URI"], RDF.type, OWL.Class))
        g.add((classe_dic["class_URI"], RDFS.label, Literal(classes[0])))
        g.add((classe_dic["class_URI"], RDFS.comment,Literal(classes[1])))

    #Parse Attributes sheet -> ontology data properties
    for attributes in book["Attributes"][1:]: 
        if attributes[3]!="": #reusing an existing ontology
            attribute_URI=URIRef(attributes[3])
        else: #ontology data properties
            attribute_URI=URIRef(str(cl.get(attributes[0])["class_URI"])+"#"+convertToCamelcase(unidecode(attributes[1]).split()))    
            g.add((attribute_URI, RDF.type, OWL.DatatypeProperty))
            g.add((attribute_URI, RDFS.label, Literal(attributes[1])))
            g.add((attribute_URI, RDFS.comment, Literal(attributes[2])))
            g.add((attribute_URI,RDFS.domain,cl.get(attributes[0])["class_URI"]))

    #Parse Relationships sheet -> ontology object properties
    for relationships in book["Relationships"][1:]:
        if relationships[4]!="":
            relationship_URI = URIRef(relationships[4])
        else:
            relationship_URI = URIRef(ontology_namespace+ convertToCamelcase(unidecode(relationships[2]).split()))
            g.add((relationship_URI, RDF.type, OWL.ObjectProperty)) 
            g.add((relationship_URI,RDFS.label, Literal(relationships[2])))
            g.add((relationship_URI,RDFS.comment, Literal(relationships[3])))
            g.add((relationship_URI,RDFS.domain,cl.get(relationships[0])["class_URI"]))
            g.add((relationship_URI,RDFS.range,cl.get(relationships[1])["class_URI"]))
    
    print(g.serialize(format="turtle"))

    #Parse Enumerations sheet

    #Create SPARQL-Generate query


    #     body_part1 =body_part1+"<"+attributeURI +">"+ " ?" +class_attribut_ref_link[4]+";\n"
        
    #     #URI minting strategy
    #     if class_attribut_ref_link[5]=="yes": class_instance_identifier=class_attribut_ref_link[4]
    #     body_part2=body_part2+bind_line.format(column_source=class_attribut_ref_link[4])+"\n"
            

    # template_GeoJSON=template_GeoJSON.format(generated_class_variable=generated_class_variable,class_type= class_type,body_part1=body_part1,dataset_link=dataset_link,class_instance_base_link=class_instance_base_link,class_instance_identifier=class_instance_identifier,body_part2=body_part2)        

    # with open(result_path+"query_GeoJSON.rq","w") as fichier_out1, open(result_path+"ontology.ttl","w") as fichier_out2 :
    #     fichier_out1.write(template_GeoJSON)
    #     fichier_out2.write(g.serialize(format="turtle"))


# ------------------------------------------------------------------------------------------------------------------



dataset_link = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=adr_voie_lieu.adrcomgl&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171"
class_instance_base_link = "https://data.grandlyon.com/id/commune/"
file_name="/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/input.ods"
ontology_namespace = "https://data.grandlyon.com/ontology/"
path="/home/sarra/Documents/Doctorat/Python/communeScript/New/Semantic-lifting/test/"

createGeoJSONQueryForSPARQLGenerate(dataset_link,class_instance_base_link,file_name, path, ontology_namespace)