import json
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(script_dir, "nit_placement_stats_with_sources.txt")

def search_placements_for_nit(college_list, **kwargs):
    try:
        context_for_llm = ""
        sources = ""
        if type(college_list) is not list:
            college_list = [college_list]


        with open(file_path, 'r') as f:
            placement_stats = json.loads(f.read())
        for college in college_list:
            college_data = placement_stats.get(college)
            first_element = college_data.pop(0)
            links_list = first_element["source"].split(",")
            for link in links_list:
                 sources += f'<a href={link} target="_blank" > {college}({first_element["year"]}) </a> \n'
            context_for_llm += f"{college} : \n {college_data} \n\n"

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


search_placements_for_nit_schema = {
    "type": "function",
    "function": {
        "name": "search_placements_for_nit",
        "description": "Searches for placement statistics and data for NIT colleges. IMPORTANT: Only pass the base college name (e.g., 'NIT Trichy'), NOT with branch/department names (e.g., NOT 'NIT Trichy Mechanical'). The function will return all placement data for the college, which may include branch-wise breakdowns.",
        "parameters": {
            "type": "object",
            "properties": {
                "college_list": {
                    "oneOf": [
                        {
                            "type": "string",
                            "description": "A single NIT college name (base name only, without branch/department)",
                            "enum": ["NIT Trichy", "NIT Surathkal", "NIT Rourkela", "NIT Warangal", "NIT Calicut",
                                     "VNIT Nagpur", "MNIT Jaipur", "NIT Kurukshetra", "NIT Silchar", "NIT Durgapur",
                                     "MNIT Allahabad", "NIT Jalandhar", "SVNIT Surat", "MANIT Bhopal", "NIT Meghalaya",
                                     "NIT Raipur", "NIT Agartala", "NIT Goa", "NIT Jamshedpur", "NIT Patna"
                                     ],
                            "examples": ["NIT Trichy", "VNIT Nagpur", "MNIT Allahabad"]
                        },
                        {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["NIT Trichy", "NIT Surathkal", "NIT Rourkela", "NIT Warangal", "NIT Calicut",
                                     "VNIT Nagpur", "MNIT Jaipur", "NIT Kurukshetra", "NIT Silchar", "NIT Durgapur",
                                     "MNIT Allahabad", "NIT Jalandhar", "SVNIT Surat", "MANIT Bhopal", "NIT Meghalaya",
                                     "NIT Raipur", "NIT Agartala", "NIT Goa", "NIT Jamshedpur", "NIT Patna"
                                     ]
                            },
                            "description": "A list of NIT college names (base names only, without branch/department specifications)",
                            "minItems": 1,
                            "maxItems": 10,
                            "examples": [
                                ["NIT Patna", "VNIT Nagpur"],
                                ["SVNIT Surat", "MANIT Bhopal","MNIT Jaipur"],
                                ["NIT Trichy", "NIT Surathkal", "MNIT Allahabad"],
                                ["NIT Rourkela", "NIT Meghalaya",
                                     "NIT Raipur", "NIT Warangal", "NIT Goa", "NIT Jamshedpur", "NIT Patna"]
                            ]
                        }
                    ],
                    "description": "Either a single NIT college name or a list of NIT college names. Use ONLY the base college name (e.g., 'NIT Trichy'), do NOT include branch or department names. Available colleges: NIT Trichy, NIT Surathkal, NIT Rourkela, NIT Warangal, NIT Calicut,VNIT Nagpur, MNIT Jaipur,NIT Kurukshetra, NIT Silchar, NIT Durgapur,MNIT Allahabad, NIT Jalandhar, SVNIT Surat, MANIT Bhopal, NIT Meghalaya, NIT Raipur, NIT Agartala, NIT Goa, NIT Jamshedpur, NIT Patna"
                }
            },
            "required": ["college_list"]
        }
    }
}

 