class Utils:

    @staticmethod
    def contains(needle, haystack, search_type='contains', options=[]):
        if not type(needle) == list:
            needle = [needle]
        if 'lowercase' in options:
            needle = [x.lower() for x in needle]
            haystack = haystack.lower()
        if type(haystack) != str:
            needle = [x.encode() if type(x) == str else x for x in needle]
        match = None
        for n in needle:
            fixed_needle = n.decode() if type(n) != str else n
            if search_type == 'contains':
                return fixed_needle if n in haystack else None
            if search_type == 'contains_all':
                if n not in haystack:
                    return None
                else:
                    match = fixed_needle
            if search_type == 'contains_any':
                if n in haystack:
                    match = fixed_needle
                    break
        return match