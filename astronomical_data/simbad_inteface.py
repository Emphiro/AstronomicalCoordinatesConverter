from astroquery.simbad import Simbad

object_names = [
"α Pavonis",
"Albireo",
"δ Cyg",
"η Carinae",
# "LMC", For some reason this interferes with all following requests
"Veil Nebula",
"Leo Triplet",
# "Markarian's Chain", 
"NGC4402",
"Stephan's Quintet",
"M1",
"M13",
"M16",
"M20",
"M31",
"M33",
"M35",
"M42",
"M45",
"M51",
"M57",
"M63",
"M78",
"M81",
"M82",
"M95",
"M96",
"M97",
"M101",
"M108",
"NGC281",
"NGC869",
"NGC884",
"NGC1499",
"NGC2237",
"NGC2264",
"NGC3521",
"NGC4438",
"NGC4565",
"NGC4631",
"NGC5139",
"NGC7000",
"NGC7023",
"NGC7293",
"NGC7331",
"NGC7635",
"IC405",
"IC434",
"IC443",
"IC1396",
"IC1805",
"IC1848",
"IC5146",
"Melotte 15",
]


def parse(ra_dec: str) -> (float, float, float):
    entries = ra_dec.split(" ")
    mapped = tuple(map(float, entries))
    if len(entries) == 3:
        return mapped
    if len(entries) == 2:
        return (*mapped, 0.0)
    assert len(entries) == 1
    return (*mapped, 0.0, 0.0)


def get_objects(names: list = None):
    if names is None:
        names = object_names

    print(names)
    object_table = Simbad.query_objects(names)
    objects = []
    if object_table is None:
        return None
    print(object_table)
    print("!")
    for i, name in enumerate(names):
        object = object_table[i]
        ra, dec = parse(object['RA']), parse(object['DEC'])
        values = (name, ra, dec)
        objects.append(values)
    return objects


if __name__ == "__main__":
    table = Simbad.query_objects(object_names)
    print(table)

    for i, name in enumerate(object_names):
        object = table[i]
        print(f"{object}")
        print(f"{name}: {object['RA']}, {object['DEC']}")
        ra, dec = parse(object['RA']), parse(object['DEC'])
        print(f"ra: {ra}, dec: {dec}")