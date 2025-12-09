# funcao interna de associar_ptos_com_fotos.py

import xml.etree.ElementTree as ET

def ler_poligonos(kml_file):
  # Load the KML file
  # kml_file = "your_kml_file.kml"
  poligonos = {}
  tree = ET.parse(kml_file)
  root = tree.getroot()

  # Define a namespace dictionary for KML elements
  ns = {"kml": "http://www.opengis.net/kml/2.2"}

  # Iterate through all Placemark elements in the KML file
  placemarks = root.findall(".//kml:Placemark", namespaces=ns)
  for placemark in placemarks:
      name_element = placemark.find(".//kml:name", namespaces=ns)
      coords_element = placemark.find(".//kml:coordinates", namespaces=ns)
      name = name_element.text.strip()
      if name_element is not None and coords_element is not None:
          # Extract Placemark name and coordinates
          coords_text = coords_element.text.strip()
          coords_list = coords_text.split()

          # Create an array of tuples with (longitude, latitude)
          placemark_data = []
          for coord in coords_list:
              lon, lat, _ = coord.split(",")  # Assuming coordinates are in lon,lat,alt format
              placemark_data.append((float(lat), float(lon)))

          # Append the data for this Placemark to the list
          poligonos[name] = placemark_data

  return poligonos