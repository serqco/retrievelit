# dict key is the str that gets searched for by args
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
    'EnCyCris': {  # small venue, included for testing purposes
        'name': 'Workshop on Engineering and Cybersecurity of Critical Systems (EnCyCriS)',
        'type': 'conference',
        'metadata_sources': {
            'dblp': {
                'type': 'conf',
                'acronym': 'icse-encycris'
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
