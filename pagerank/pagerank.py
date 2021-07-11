import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prob_dist = dict()
    link_count = len(corpus[page])
    non_link_count = len(corpus) - link_count
    
    if link_count > 0:
        # if statement stops div by zero error
        linked_prob = damping_factor / link_count
    
    non_linked_prob = (1 - damping_factor) / non_link_count
    if link_count == 0:
        non_linked_prob = 1 / non_linked_prob

    for link in corpus:
        if link in corpus[page]:
            # Even though linked_prob is defined in an if staement
            # this code won't execute for pages with no links so
            # this is not a concern
            prob_dist[link] = linked_prob
        else:
            prob_dist[link] = non_linked_prob
    
    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    visit_count = {page:0 for page in corpus}

    # First Sample
    cur_page = random.choice(list(corpus.keys()))
    visit_count[cur_page] = visit_count[cur_page] + 1

    # Subsequent samples
    for sample in range(n - 1):
        prob_dist = transition_model(corpus, cur_page, damping_factor)
        # Strangely .keys() does not return a list so it must be casted
        pages = list(prob_dist.keys())
        probs = prob_dist.values()

        # choices() picks from array based on weights (returns a list).
        # alternatively, you could use list comp and random.choice()
        # but that approach seems more memory intensive
        cur_page = random.choices(population=pages, weights=probs)[0]
        visit_count[cur_page] = visit_count[cur_page] + 1
    
    return {page:count/n for (page, count) in visit_count.items()}


def link_to_pages(corpus, linkless_pages):
    """
    Returns a dictionary that takes a page and returns
    a list of other pages that link to it

    Based on code from https://tinyurl.com/27h4hd5s
    """
    inverted = {page:list() for page in corpus}
    for page in corpus:
        for link in corpus[page]:
            inverted[link].append(page)
        # We're treating linkess pages as having a link for every page
        # so we add the all the linkless pages to the list
        inverted[page] += linkless_pages
    return inverted
        


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    page_ranks = {link:1/N for link in corpus}
    linkless = [page for page in corpus if len(corpus[page]) == 0]
    # min_change tracks if all page ranks changed by <= 0.001
    min_change = False
    # shows every page that links to the key (a page)
    links_to = link_to_pages(corpus, linkless)
    # the constant chance a surfer will randomly go to another page
    random_choice_prob = (1 - damping_factor) / N

    while not min_change:
        min_change = True
        # We only update the page_ranks until after one iteration
        # so we must save the updated page_ranks for after
        new_page_ranks = dict()

        for link in corpus:
            old_pr = page_ranks[link]
            # The chance the current page is reached by a surfer
            # clicking a link on another page
            link_to_prob = 0

            # Loop through all pages that link to current page
            for page in links_to[link]:
                num_links = len(corpus[page])
                pr = page_ranks[page]
                if num_links == 0:
                    # If a page is linkless we treat it like it links
                    # to all pages.
                    num_links = N
                prob = damping_factor * (pr / num_links)
                link_to_prob += prob

            new_pr = link_to_prob + random_choice_prob
            # If any page rank changes by more than 0.001, we must
            # go through another iteration
            if abs(new_pr - old_pr) > 0.001:
                min_change = False
            new_page_ranks[link] = new_pr
        # Update page_ranks after a full iteration
        page_ranks = new_page_ranks

    return page_ranks


if __name__ == "__main__":
    main()
