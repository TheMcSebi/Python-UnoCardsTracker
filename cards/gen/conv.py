import cv2

sx = 242
sy = 362

img = cv2.imread('UNO_cards_deck.png', cv2.IMREAD_UNCHANGED) # flag is required for alpha channel

lookup_x = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "skip", "reverse", "draw2", "wild"] # 14 columns
lookup_y = ["red", "yellow", "green", "blue", "red2"] # 5 rows
        
for iy in range(0, len(lookup_y)):
    y1 = iy*sy - 2*iy
    y2 = iy*sy + sy - 2*iy
    for ix in range(0, len(lookup_x)):
        x1 = ix*sx - 2*ix
        x2 = ix*sx + sx - 2*ix

        print(x1, x2, y1, y2)
        print(x2-x1, y2-y1)

        filename = f"{lookup_y[iy]}_{lookup_x[ix]}"
        if filename == "red2_wild":
            filename = "wildplus4"
        elif "wild" in filename:
            filename = "wild"
        elif "red2" in filename:
            continue

        myimg = img[y1:y2, x1:x2]

        cv2.imwrite(f"../{filename}.png", myimg)