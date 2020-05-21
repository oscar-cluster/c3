PREFIX=
CONTRIBDIR=$(PREFIX)/contrib
FILES= add_user \
	c3_conf_manager \
	enable_clusters \
	push_passwd \
	sync_date

all:

install:
	install -d $(CONTRIBDIR)
	install -m 744 $(FILES) $(CONTRIBDIR)
