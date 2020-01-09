import segmentation
import os


def check_files(dn):
    ret = set()
    for _, _, files in os.walk(dn):
        for f in files:
            ret.add(f[2:])
    return ret


if __name__ == "__main__":

    # specify pages to test
    base = "/home/cramaker/Documents/master_thesis/test_data/"

    fileset = check_files(base)
    for i in fileset:

        files = ["a." + i]
        files = filter(lambda x: os.path.exists(base + x), files)
        # open all needed files
        pages = [open(base + f).read() for f in files]

        # strip form useless tags and change to segments
        ready = map(lambda x: segmentation.prep(x), pages)

        all_segs = segmentation.block_fusion(ready, 0.3)
        # print all_segs
        # for a in all_segs:
            # print a[0].tags[0].prettify()

        # visualize
        for i in range(0, len(all_segs)):
            segmentation.visualize(all_segs[i], "/home/cramaker/Documents/" + files[i])
