import sys

from windchill_api_lookup.parser.ptc_javadoc import (
    parse_class_metadata,
    parse_methods,
    read_class_html,
)


def main():
    if len(sys.argv) not in (3, 4):
        print("Usage:")
        print(
            "  windchill-api-lookup "
            "<javadoc-zip> "
            "<qualified-class-name> "
            "[method-name]"
        )
        return

    zip_path = sys.argv[1]
    qualified_class_name = sys.argv[2]

    html = read_class_html(
        zip_path,
        qualified_class_name,
    )

    if len(sys.argv) == 3:
        metadata = parse_class_metadata(html)

        print("Class Metadata")
        print("----------------")
        print(f"Class:      {qualified_class_name}")
        print(f"Title:      {metadata['title']}")
        print(f"Package:    {metadata['package']}")
        print(f"Supported:  {metadata['supported']}")
        print(f"Extendable: {metadata['extendable']}")

        return

    method_name = sys.argv[3]

    methods = parse_methods(
        html,
        method_name,
    )

    print(
        f"Methods: {qualified_class_name}.{method_name}"
    )

    print(
        f"Overloads: {len(methods)}"
    )

    print()

    for index, method in enumerate(
        methods,
        start=1,
    ):
        print(f"[{index}]")
        print(
            f"ID:         {method['javadoc_id']}"
        )
        print(
            f"Signature:  {method['signature']}"
        )
        print(
            f"Return:     {method['return_type']}"
        )
        print(
            f"Supported:  {method['supported']}"
        )
        print(
            f"Deprecated: {method['deprecated']}"
        )
        print(
            f"Throws:     {', '.join(method['throws'])}"
        )
        print()