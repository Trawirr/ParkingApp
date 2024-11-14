import argparse
import os

class Date:
    def __init__(self, date_str: str, separator: str = '_') -> None:
        if date_str is not None:
            self.time = [int(d) for d in date_str.split('.')[0].split(separator)]
            self.ext = f".{date_str.split('.')[-1]}"
        else:
            self.time = [0 for i in range(5)]    
        # print(f"Date object created: {self.time=}")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Date):
            return self.time == other.time
        return False
    
    def __gt__(self, other: object) -> bool:
        # print(f"{self.time} > {other.time}")
        if isinstance(other, Date):
            for i in range(len(self.time)):
                if self.time[i] < other.time[i]:
                    return False
                elif self.time[i] > other.time[i]:
                    return True
            return False
        return False
    
    def __add__(self, other: object) -> object:
        max_vals = [10000, 12, 30, 24, 60]
        time_tmp = self.time
        if isinstance(other, int):
            time_tmp[-1] += other

        for i in range(len(time_tmp) - 1, 0, -1):
            time_tmp[i - 1] += time_tmp[i] // max_vals[i]
            time_tmp[i] %= max_vals[i]

        new_d = Date(None)
        new_d.time = time_tmp
        new_d.ext = self.ext
        return new_d
    
    def __str__(self) -> str:
        return '_'.join([str(t) if t >= 10 else '0' + str(t) for t in self.time]) + self.ext

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="path to directory with files to be split")
    parser.add_argument("-o", "--output", type=str, help="path to output directory")
    parser.add_argument("-t", "--time", type=int, default=10, help="time in minutes between next samples")
    return parser.parse_args()

def split_filename(filename):
    k = filename.split("_")[0]
    return k, filename[len(k) + 1:]

if __name__ == "__main__":
    args = parse_args()
    path = args.path
    step = args.time
    output_path = args.output
    print(f"{path=}")
    # directory = os.fsencode(path)

    # print(f"{directory=}")
    
    # for i, file in enumerate(os.listdir(directory)):
    #     filename = os.fsencode(file)
    #     if filename.endswith(b".png") or filename.endswith(b".jpg"):
    #         print(i, filename)

    filenames = {}
    for i, filename in enumerate(os.listdir(path)):
        f = os.path.join(path, filename)
        if os.path.isfile(f) and filename.endswith(".jpg"):
            k, v = split_filename(filename)
            if k not in filenames:
                filenames[k] = []
            filenames[k].append(v)

    for k, v in filenames.items():
        filenames[k] = sorted(v)

    dates = {}

    for k in filenames:
        dates[k] = [Date(filenames[k][0]), Date(filenames[k][-1])]

    # find limits
    curr_date = min([dates[k][0] for k in dates.keys()])
    max_date = min([dates[k][1] for k in dates.keys()])

    # fix directories
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    num_of_classes = len(dates.keys())
    while not curr_date > max_date:
        for k in dates.keys():
            filename = str(curr_date)
            if filename not in filenames[k]:
                print(f"{str(curr_date)} not in {k=}")
                curr_date += 1
                break
        else:
            for k in dates.keys():
                filename = k + "_" + str(curr_date)
                os.popen(f'copy {os.path.join(path, filename)} {os.path.join(output_path, filename)}')
                print(f'copy {os.path.join(path, filename)} {os.path.join(output_path, filename)}')
            curr_date += step

