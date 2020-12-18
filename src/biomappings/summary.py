# -*- coding: utf-8 -*-

"""Generate a summary for the Biomappings website."""

import itertools as itt
import os
from collections import Counter
from typing import Iterable, Mapping, Optional

import click
import yaml

__all__ = [
    'export',
]


@click.command()
def export():
    """Create export data file."""
    from biomappings.resources import load_mappings, load_predictions, load_false_mappings

    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, os.pardir, os.pardir, 'docs', '_data', 'summary.yml')

    true_mappings = load_mappings()
    false_mappings = load_false_mappings()
    rv = {
        'positive': _get_counter(true_mappings),
        'negative': _get_counter(false_mappings),
        'predictions': _get_counter(load_predictions()),
        'contributors': _get_contributors(itt.chain(true_mappings, false_mappings)),
    }
    rv.update({
        f'{k}_mapping_count': sum(e['count'] for e in rv[k])
        for k in ('positive', 'negative', 'predictions')
    })
    rv.update({
        f'{k}_prefix_count': len(set(itt.chain.from_iterable((e['source'], e['target']) for e in rv[k])))
        for k in ('positive', 'negative', 'predictions')
    })
    with open(path, 'w') as file:
        yaml.safe_dump(rv, file, indent=2)


def _get_counter(mappings: Iterable[Mapping[str, str]]):
    counter = Counter()
    for mapping in mappings:
        source, target = mapping['source prefix'], mapping['target prefix']
        if source > target:
            source, target = target, source
        counter[source, target] += 1
    return [
        dict(source=source, target=target, count=count)
        for (source, target), count in counter.most_common()
    ]


def _get_contributors(mappings: Iterable[Mapping[str, str]]):
    counter = Counter(
        _get_source(mapping['source'])
        for mapping in mappings
    )
    return [
        dict(orcid=orcid, count=count) if orcid else dict(count=count)
        for orcid, count in counter.most_common()
    ]


def _get_source(source: str) -> Optional[str]:
    if source.startswith('orcid:'):
        return source[len('orcid:'):]


if __name__ == '__main__':
    export()
