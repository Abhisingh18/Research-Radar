from research_radar.sources.arxiv import _parse_feed

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <updated>2024-01-01T12:00:00Z</updated>
    <published>2024-01-01T12:00:00Z</published>
    <title>A Great Paper About Agents</title>
    <summary>This paper studies agents.</summary>
    <author><name>Jane Doe</name></author>
    <author><name>John Smith</name></author>
    <category term="cs.AI" />
  </entry>
</feed>
"""


def test_parse_feed_extracts_single_paper():
    papers = _parse_feed(SAMPLE_FEED)

    assert len(papers) == 1
    paper = papers[0]
    assert paper.title == "A Great Paper About Agents"
    assert paper.authors == ["Jane Doe", "John Smith"]
    assert paper.id == "http://arxiv.org/abs/2401.00001v1"
    assert paper.categories == ["cs.AI"]
    assert paper.source == "arxiv"


def test_parse_feed_handles_empty_feed():
    empty_feed = '<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"></feed>'
    assert _parse_feed(empty_feed) == []
