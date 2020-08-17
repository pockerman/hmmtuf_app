import matplotlib.pyplot as plt

def main():

    x = [0.0, 1.0, 2.0, 3.0, 4.0]
    y = [0.0, 1.0, 2.0, 3.0, 4.0]
    # plt.scatter(no_wga_obs, wga_obs, color=colors)
    plt.scatter(x, y, color='red')

    plt.xlabel("NO-WGA")
    plt.ylabel("WGA")
    plt.title("my plot")
    plt.legend(loc='upper right', title="States")
    plt.xlim((0.0, 5.0))
    plt.ylim((0.0, 5.0))

    #plt.show()
    plt.savefig("my_file.png", bbox_inches='tight', dpi=72)
    plt.close()

if __name__ == '__main__':
    main()