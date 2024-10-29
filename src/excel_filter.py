class ExcelCategorizer:

    def filter_new_links(self, new_links, existing_links):
        return [link for link in new_links if link not in existing_links]