import sys
import xml.etree.ElementTree as ET
import os
import django

topic_subset_file = "topic_file.csv"
topic_file = "topics.xml"


def add_topic(topic_id, title, description, narrative):

    print(title)
    t = Topic.objects.get_or_create(topic_id=topic_id)[0]
    print(t)
    t.title = title
    t.description = description
    t.narrative = narrative
    t.save()
    print(f"Added: {t}")


def populate(topic_file):
    """
    This reads in a TREC_TOPIC_FILE (assumed to be XML) - compatiable with WAPO, CC , etc.
    """
    tree = ET.parse(topic_file)
    tree_root = tree.getroot()
    next_root = tree_root.getchildren()

    topics = {}

    for child in next_root:
        grand_child = []
        grand_child = child.getchildren()
        for great_grand_child in grand_child:
            if great_grand_child.tag == "title":
                title = str(great_grand_child.text.strip("\n"))
            if great_grand_child.tag == "num":
                topic_num = great_grand_child.text[8:].strip(" ")
            if great_grand_child.tag == "desc":
                description = great_grand_child.text[14:]
            if great_grand_child.tag == "narr":
                narrative = great_grand_child.text[11:]

        topics[topic_num] = {
            "title": title,
            "description": description,
            "narrative": narrative,
        }

    with open(topic_subset_file, "r") as f:
        topic_set = []
        for line in f:
            topic_set = list(line.strip("\n").split(","))

    for topic in topic_set:

        print(f"added {topic}")
        print(
            f'{topic} -  {topics[topic]["title"]}, {topics[topic]["description"]}, {topics[topic]["narrative"]}'
        )

        add_topic(
            int(topic),
            topics[topic]["title"],
            topics[topic]["description"],
            topics[topic]["narrative"],
        )


if __name__ == "__main__":
    print("Starting Topic Population Script")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "card_model.settings")
    sys.path.append("../")
    django.setup()
    from assessment_page.models import Topic

    populate(topic_file)
