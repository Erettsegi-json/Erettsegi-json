import csv
import subject_dict

csvfile = open('processed.csv', 'w', newline='')
csvfile_links = open('processed_links.csv', 'w', newline='')
csvwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
csvwriter_links = csv.writer(csvfile_links, delimiter=';', quoting=csv.QUOTE_NONE)

different = dict()
with open("day.csv", "r") as f:
    for line in f:
        if line.strip() == '':
            continue
        end = line.split('/')[-1].split('.')[0]
        segments = end.split('_')
        data = []
        if segments[0] == 'k':
            data.append('középszint')
        elif segments[0] == 'e':
            data.append('emeltszint')
        else:
            print("error")

        if len(segments) < 4:
            print(line)
            continue
        subject_code = '_'.join(segments[1:-2])
        if subject_code not in subject_dict.subject:
            print(line)
            continue
        data.append(subject_dict.subject[subject_code])
        date_code = segments[-2]
        data.append('20'+date_code[:2])
        if date_code[2:] in ['okt', 'nov']:
            data.append('ősz')
        elif date_code[2:] in ['maj', 'febr']:
            data.append('tavasz')
        else:
            print(line)
            continue
        if segments[-1] in ['fl', 'fl2']:
            data.append("feladatlap")
        elif segments[-1] in ['ut']:
            data.append("megoldas")
        else:
            print(line)
            continue
        data.append("https://oktatas.hu"+line.strip())
        if ';'.join(data[:-2]) not in different:
            different[';'.join(data[:-2])] = data[-1]
        else:
            different[';'.join(data[:-2])] += ' ' + data[-1]
        csvwriter.writerow(data)
for key in sorted(different, reverse=True, key=lambda key: key.split(';')[2:4]):
    csvwriter_links.writerow(key.split(';')+[different[key]])
