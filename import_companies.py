import csv

from db_helper import Session, Company

path = 'companies.csv'


def import_data(path):
    with open(path) as f:
        print(1)
        line_count = 0
        reader = csv.reader(f, delimiter=';')
        session = Session()
        for row in reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                company = Company(
                    gvkey=row[0],
                    name=row[1],
                    factiva_name=row[2],
                    factiva_code=row[3],
                )
                session.add(company)
        session.commit()
        print(f'Processed {line_count} lines.')


if __name__ == '__main__':
    import_data(path)
