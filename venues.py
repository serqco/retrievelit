# dict key is the str that gets searched for by args
# acronym used for dblp URL right now
# type_url are the types for dblp token
VENUES = {
    'EMSE': {
        'name': 'Empirical Software Engineering',
        'type': 'journal',
        'metadata_sources': {
            'dblp': {
                'type': 'journals',
                'acronym': 'ese'
            },
        },
    },
    'ICSE': {
        'name': 'International Conference on Software Engineering',
        'type': 'conference',
        'metadata_sources': {
            'dblp': {
                'type': 'conf',
                'acronym': 'icse'
            },
        },
    },
    'IST': {
        'name': 'Information and Software Technology',
        'type': 'journal',
        'metadata_sources': {
            'dblp': {
                'type': 'journals',
                'acronym': 'infsof'
            },
        },
    },
    'TOSEM': {
        'name': 'ACM Transactions on Software Engineering and Methodology',
        'type': 'journal',
        'metadata_sources': {
            'dblp': {
                'type': 'journals',
                'acronym': 'tosem'
            },
        },
    },
    'TSE': {
        'name': 'IEEE Transactions on Software Engineering',
        'type': 'journal',
        'metadata_sources': {
            'dblp': {
                'type': 'journals',
                'acronym': 'tse'
            },
        },
    }
}
