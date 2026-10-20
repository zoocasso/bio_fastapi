"""Reading a person's genotypes into the rows the annotation pipeline joins on.

Two inputs are supported: a single-sample VCF, and the tab-separated raw export of a genotyping
chip (rsID, chromosome, position, genotype; lines starting with # are comments).
"""

import logging
import re
from pathlib import Path

import pandas as pd
import vcf

log = logging.getLogger(__name__)

SAMPLE_FIELDS = ("GT", "AD", "DP", "GQ", "PL")


def _alleles(genotype: str) -> tuple[str, str]:
    """ "A/G" or "A|G" -> ("A", "G"); a haploid call such as "A" counts as homozygous."""
    parts = re.split(r"[/|]", genotype)
    return (parts[0], parts[0]) if len(parts) == 1 else (parts[0], parts[1])


def read_vcf(path: Path) -> pd.DataFrame:
    rows, skipped = [], 0
    with open(path) as f:
        for record in vcf.Reader(f):
            call = record.samples[0]
            if not call.called or call.gt_bases is None:
                skipped += 1
                continue
            allele_1, allele_2 = _alleles(call.gt_bases)
            alt = str(record.ALT[0])
            data = call.data
            rows.append(
                {
                    "chrom": str(record.CHROM),
                    "pos": int(record.POS),
                    "id": str(record.ID),
                    "ref": record.REF,
                    "alt": alt,
                    "qual": str(record.QUAL),
                    "filter": ";".join(record.FILTER) if record.FILTER else "PASS",
                    "info": str(record.INFO),
                    "format": str(record.FORMAT),
                    "sample_data": ";".join(
                        str(getattr(data, f)) for f in SAMPLE_FIELDS if getattr(data, f, None) is not None
                    ),
                    "allele_1": allele_1,
                    "allele_2": allele_2,
                    # the key every reference table is joined on
                    "connect_key": f"{record.CHROM}-{record.POS}-{record.REF}-{alt}",
                }
            )
    if skipped:
        log.info("%s: skipped %d records without a called genotype", path.name, skipped)
    return pd.DataFrame(rows)


def read_array(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep="\t",
        comment="#",
        names=["rsID", "CHR", "POS", "genotype"],
        dtype={"rsID": str, "CHR": str, "POS": int, "genotype": str},
    )
    # "--" is a no-call on most chips; it stays in so the row count matches the export
    alleles = df["genotype"].fillna("--").map(lambda g: (g[0], g[0]) if len(g) == 1 else (g[0], g[1]))
    df["allele_1"] = alleles.str[0]
    df["allele_2"] = alleles.str[1]
    return df[["CHR", "POS", "rsID", "allele_1", "allele_2"]]
