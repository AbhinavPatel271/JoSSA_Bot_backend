import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(script_dir, "IIT_placement_stats.txt")

def search_placements_for_iit(college_list, **kwargs):
    try:
        sources = "\n"
        context_for_llm = ""
        if type(college_list) is not list:
            college_list = [college_list]

        with open( file_path , 'r') as f:
            placement_stats = json.loads(f.read())

        for college in college_list:
                college_data = placement_stats.get(college)
                if college != "IIT Delhi":
                    first_element = college_data.pop(0)
                    links_list = first_element["source"].split(",")
                    for link in links_list:
                        sources += f'<a href={link} target="_blank" > {college}({first_element["year"]}) </a> \n'
                        context_for_llm += f"{college} : \n {college_data} \n\n"

                else:
                    sources += ""
                    context_for_llm += f"{college}: \n No Data Available \n\n"
        print("CONTEXT FOR LLM : " , context_for_llm)
        print("LINKS : " , sources)

        return {
            "success": True,
            "answer": context_for_llm,
            "sources": sources
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


search_placements_for_iit_schema = {
    "type": "function",
    "function": {
        "name": "search_placements_for_iit",
        "description": "Searches for placement statistics and data for IIT colleges. IMPORTANT: Only pass the base college name (e.g., 'IIT Bombay'), NOT with branch/department names (e.g., NOT 'IIT Bombay Mechanical'). The function will return all placement data for the college, which may include branch-wise breakdowns.",
        "parameters": {
            "type": "object",
            "properties": {
                "college_list": {
                    "oneOf": [
                        {
                            "type": "string",
                            "description": "A single IIT college name (base name only, without branch/department)",
                            "enum": ["IIT BHU", "IIT Hyderabad", "IIT ISM Dhanbad", "IIT Jammu", "IIT Jodhpur",
                                     "IIT Kanpur", "IIT Tirupati", "IIT Bhubaneshwar", "IIT Guwahati", "IIT Bombay",
                                     "IIT Indore", "IIT Bhilai", "IIT Dharwad", "IIT Gandhinagar", "IIT Goa",
                                     "IIT Kharagpur", "IIT Mandi", "IIT Pallakkad", "IIT Patna", "IIT Roorkee",
                                     "IIT Ropar", "IIT Madras", "IIT Delhi" , "IIT (BHU) Varanasi"],
                            "examples": ["IIT Bombay", "IIT Kanpur", "IIT Madras"]
                        },
                        {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["IIT BHU", "IIT Hyderabad", "IIT ISM Dhanbad", "IIT Jammu", "IIT Jodhpur",
                                         "IIT Kanpur", "IIT Tirupati", "IIT Bhubaneshwar", "IIT Guwahati", "IIT Bombay",
                                         "IIT Indore", "IIT Bhilai", "IIT Dharwad", "IIT Gandhinagar", "IIT Goa",
                                         "IIT Kharagpur", "IIT Mandi", "IIT Pallakkad", "IIT Patna", "IIT Roorkee",
                                         "IIT Ropar", "IIT Madras", "IIT Delhi"]
                            },
                            "description": "A list of IIT college names (base names only, without branch/department specifications)",
                            "minItems": 1,
                            "maxItems": 10,
                            "examples": [
                                ["IIT Bombay", "IIT Madras"],
                                ["IIT Kanpur", "IIT Kharagpur", "IIT Roorkee"],
                                ["IIT Guwahati", "IIT Hyderabad", "IIT Indore"]
                            ]
                        }
                    ],
                    "description": "Either a single IIT college name or a list of IIT college names. Use ONLY the base college name (e.g., 'IIT Bombay'), do NOT include branch or department names. Available colleges: IIT BHU, IIT Hyderabad, IIT ISM Dhanbad, IIT Jammu, IIT Jodhpur, IIT Kanpur, IIT Tirupati, IIT Bhubaneshwar, IIT Guwahati, IIT Bombay, IIT Indore, IIT Bhilai, IIT Dharwad, IIT Gandhinagar, IIT Goa, IIT Kharagpur, IIT Mandi, IIT Pallakkad, IIT Patna, IIT Roorkee, IIT Ropar, IIT Madras"
                }
            },
            "required": ["college_list"]
        }
    }
}
 