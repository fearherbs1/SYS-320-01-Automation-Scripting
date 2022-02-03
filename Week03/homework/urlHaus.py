import csv  # import the csv lib
import re  # imports regex lib Fix: This was not previously imported and was needed

# define our urlhGusOpen function
# Fix: replace "1" with "l" in name
def urlHausOpen(filename, searchTerm):

    # Opens our csv file.
    # Fix: indentation, change filename within open statement to var from string, change while to with
    with open(filename) as f:

        # reads our csv content from the file. F
        # Fix: remove double "=" replace csv.review() with csv.reader(), replace filename with F, indentation
        contents = csv.reader(f)

        # loop through the first 9 elements of contents "_" always the data within it from the last operation, aka
        # "contents" in this case.
        # Fix: Indentation.
        for _ in range(9):

            # Pass these first 9 elements, this is to prevent the comments from the top of the csv to being processed.
            # Fix: indentation
            next(contents)

        # Loop through each line within the csv data we imported.
        # Fix: Indentation, swap with "for keyword in searchTerm"
        for eachLine in contents:

            # Loop through all of our search terms and do the following.
            # Fix: indentation, remove "s" from "searchTerms", swap with "for eachLine in contents"
            for keyword in searchTerm:

                # Use regex to search through the URL within the selected line of the csv file for the keyword.
                # Fix: remove the unnecessary "r" and "+", Indentation
                x = re.findall(keyword, eachLine[2])

                # loop through data that we found with the regex match.
                # Fix: Indentation
                for _ in x:

                    # Don't edit this line. It is here to show how it is possible
                    # to remove the "tt" so programs don't convert the malicious
                    # domains to links that can be accidentally clicked on.

                    # Prevent dangerous links from being made clickable and assign the url matching url to a variable
                    # Fix: indentation
                    the_url = eachLine[2].replace("http", "hxxp")

                    # Set the abuse.ch link that corresponds to the matched url to a variable.
                    # Fix: indentation, replace 4 with 6 to print info link
                    the_src = eachLine[7]

                    # Print out our results nice and pretty with *'s in between them. The .format here places the
                    # value of the variables within each "{}"
                    # Fix: indentation, add missing "{}"s to print statement, change "," to ".", replace "+" with "*",
                    # concatenate printing of *'s with a "+" and place these *'s outside of the format "()"s
                    print("""
                    URL: {}
                    Info: {}
                    """.format(the_url, the_src) + '*' * 60)
