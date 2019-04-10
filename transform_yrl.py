import urllib2
import json
import requests
from xml.dom.minidom import parseString
import xml.etree.ElementTree as ET



def get_text_node_or_default(node, tag_name):
    try:
        text = node.getElementsByTagName(tag_name)[0].childNodes[0].data
    except:
        text = ''

    return text


def convert_listings_from_xml_to_json(doc):
    all_listings = doc.getElementsByTagName("hotPadsItems")[0]

    listings = all_listings.getElementsByTagName("Listing")

    listings_for_output = []

    listing_count = 0
    for listing in listings:
	listing_id = listing.getAttribute("id")
        price = listing.getElementsByTagName("price")[0].childNodes[0].data

        street_address = listing.getElementsByTagName("street")[0].childNodes[0].data
        city = listing.getElementsByTagName("city")[0].childNodes[0].data
        state = listing.getElementsByTagName("state")[0].childNodes[0].data
        zip_code = listing.getElementsByTagName("zip")[0].childNodes[0].data

        email = listing.getElementsByTagName("contactEmail")[0].childNodes[0].data
        phone = listing.getElementsByTagName("contactPhone")[0].childNodes[0].data

        bedrooms = listing.getElementsByTagName("numBedrooms")[0].childNodes[0].data
        bathrooms = listing.getElementsByTagName("numFullBaths")[0].childNodes[0].data
        half_bathrooms = listing.getElementsByTagName("numberHalfBaths")[0].childNodes[0].data

        living_area = get_text_node_or_default(listing, 'LivingArea')
        description = get_text_node_or_default(listing, 'description')
        unit = get_text_node_or_default(listing, 'unit')

        images = []

        try:
            picture_nodes = listing.getElementsByTagName('ListingPhoto')
            for picture_node in picture_nodes:
                picture_url = picture_node.getAttribute('source')
                images.append(picture_url)
        except:
            images = []

        listing = {
            'listing_id': listing_id,
            'price': price,
            'street_address': street_address,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'unit': unit,
            'bedrooms': bedrooms,
            'bathrooms': bathrooms,
            'half_bathrooms': half_bathrooms,
            'square_feet': living_area,
            'description': description,
            'email': email,
            'phone': phone,
            'images': images
        }

        listings_for_output.append(listing)
        listing_count+=1

    payload = {
        'listings': listings_for_output
    }
    print listing_count

    return payload


def download_latest_ygl_file(url):
    ygl_response = urllib2.urlopen(url)

    ygl_xml = ygl_response.read()

    return parseString(ygl_xml)

def output_datalinx_xml_from_payload(payload, filename):

    output_attributes={
            'DataLinxVersion':'1.2',
            'xmlns':'http://www.rentlinx.com',
            'xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation':'http://www.rentlinx.com http://www.rentlinx.com/Products/DataLinx/DataLinx1_2.xsd'
            }
    data = ET.Element('RentLinx', attrib=output_attributes)
    properties = ET.SubElement(data, 'Properties')
    for payloadListing in payload['listings']:
        property_node = ET.SubElement(properties, 'Property', attrib={'LocalPropertyID':payloadListing['listing_id']})
        description = ET.SubElement(property_node, 'Description').text = payloadListing['description']
        email = ET.SubElement(property_node, 'EmailAddress').text = payloadListing['email']

        address = ET.SubElement(property_node, 'Address').text = payloadListing['street_address']
        city = ET.SubElement(property_node, 'City').text = payloadListing['city']
        state = ET.SubElement(property_node, 'State').text = payloadListing['state']
        zip_code = ET.SubElement(property_node, 'Zip').text = payloadListing['zip_code']

        unit_node = ET.SubElement(property_node, 'Unit', attrib={'LocalUnitID':payloadListing['listing_id']})
        rent = ET.SubElement(unit_node, 'MinRent').text = payloadListing['price']
        unit_type = ET.SubElement(unit_node, 'UnitType').text = 'type'
        name = ET.SubElement(unit_node, 'Name').text = payloadListing['unit']
        number_of_units = ET.SubElement(unit_node, 'NumberUnits').text = '1'
        max_advertise_available = ET.SubElement(unit_node, 'MaxAdvertiseAvailable').text = '1'

        bedrooms = ET.SubElement(unit_node, 'Bedrooms').text = payloadListing['bedrooms']
        bathrooms = ET.SubElement(unit_node, 'FullBaths').text = payloadListing['bathrooms']
        half_bathrooms = ET.SubElement(unit_node, 'HalfBaths').text = payloadListing['half_bathrooms']

	for picture in payloadListing['images']:
            picture_node = ET.SubElement(unit_node, 'UnitPhoto', attrib={'ImageUrl': picture} )

    #mydata = ET.tostring(data)
    et = ET.ElementTree(data)

    #myfile = open("/home/gcaprio/griffincaprio.com/hotspot/zillow.xml", "w+")

    et.write(filename, encoding='utf-8', xml_declaration=True) 
    #myfile.write(mydata)


def output_zillow_xml_from_payload(payload, filename):
    data = ET.Element('Listings')

    for payloadListing in payload['listings']:
        listing = ET.SubElement(data, 'Listing')

        location = ET.SubElement(listing, 'Location')
        street = ET.SubElement(location, 'StreetAddress').text = payloadListing['street_address']
        city = ET.SubElement(location, 'City').text = payloadListing['city']
        state = ET.SubElement(location, 'State').text = payloadListing['state']
        zip_code = ET.SubElement(location, 'Zip').text = payloadListing['zip_code']
        unit = ET.SubElement(location, 'UnitNumber').text = payloadListing['unit']

        listing_details = ET.SubElement(listing, 'ListingDetails')
        status = ET.SubElement(listing_details, 'Status').text = 'Active'
        price = ET.SubElement(listing_details, 'Price').text = payloadListing['price']
        providerListingId = ET.SubElement(listing_details, 'ProviderListingId').text = payloadListing['listing_id']

        basic_details = ET.SubElement(listing, 'BasicDetails')
        property_type = ET.SubElement(basic_details, 'PropertyType').text = payloadListing['unit']
        bedrooms = ET.SubElement(basic_details, 'Bedrooms').text = payloadListing['bedrooms']
        bathrooms = ET.SubElement(basic_details, 'Bathrooms').text = payloadListing['bathrooms']
        half_bathrooms = ET.SubElement(basic_details, 'HalfBathrooms').text = payloadListing['half_bathrooms']
        description = ET.SubElement(basic_details, 'Description').text = payloadListing['description']

        pictures = ET.SubElement(listing, 'Pictures')
	for picture in payloadListing['images']:
               picture_node = ET.SubElement(pictures, 'Picture')
               picture_url = ET.SubElement(picture_node, 'PictureUrl').text = picture

        agent = ET.SubElement(listing, 'Agent')
        email_address = ET.SubElement(agent, 'EmailAddress').text = payloadListing['email'] 

        office = ET.SubElement(listing, 'Office')
        broker_phone = ET.SubElement(office, 'BrokerPhone').text = payloadListing['phone'] 


    #mydata = ET.tostring(data)
    et = ET.ElementTree(data)

    #myfile = open("/home/gcaprio/griffincaprio.com/hotspot/zillow.xml", "w+")

    et.write(filename, encoding='utf-8', xml_declaration=True) 
    #myfile.write(mydata)


ygl_url = 'http://www.yougotlistings.com/feed?id=sIiYXfrb6NDmBMok0ZA9PQldhV8W5uSp7jE4xCU1&code=zNnY'

doc = download_latest_ygl_file(ygl_url)

payload = convert_listings_from_xml_to_json(doc)

#zillow_filename = "/home/gcaprio/griffincaprio.com/hotspot/zillow.xml"
#datalinx_filename = "/home/gcaprio/griffincaprio.com/hotspot/datalinx.xml"

zillow_filename = "zillow.xml"
datalinx_filename = "datalinx.xml"

output_zillow_xml_from_payload(payload, zillow_filename)
output_datalinx_xml_from_payload(payload, datalinx_filename)

# hotpads: https://filenet.hotpads.com/+guides/RentalListingsFeedGuide.pdf
# zillow: https://www.zillow.com/static/pdf/feeds/ZillowBrokerFeedsTechnicalSpecV1.0.20.pdf
# showmojo: https://showmojo.com/ShowMojo_Listing_Import_API.pdf
# RentLinx https://www.rentlinx.com/docs/datalinx
