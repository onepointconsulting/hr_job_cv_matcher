from typing import List

def convert_list_to_markdown(list: List[str]) -> str:
    degree_output = ""
    for item in list:
        degree_output += f"\n- {item}"
    return degree_output