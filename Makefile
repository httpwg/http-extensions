LIBDIR := lib
USE_XSLT := true
DISABLE_RIBBON := true
GHPAGES_EXTRA = $(foreach ext,.html .txt,$(addsuffix $(ext),$(foreach draft,$(drafts),$(shell echo $(draft) | sed -e 's/draft-ietf-httpbis-//'))))

include $(LIBDIR)/main.mk

$(LIBDIR)/main.mk:
ifneq (,$(shell git submodule status $(LIBDIR) 2>/dev/null))
	git submodule sync
	git submodule update $(CLONE_ARGS) --init
else
	git clone -q --depth 10 $(CLONE_ARGS) \
	    -b master https://github.com/martinthomson/i-d-template $(LIBDIR)
endif

$(GHPAGES_EXTRA):
	ln -sf draft-ietf-httpbis-$@ $@

.PHONY: clean-extra
clean:: clean-extra

clean-extra:
	-rm -f $(GHPAGES_EXTRA)
