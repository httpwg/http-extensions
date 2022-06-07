# poke 3
LIBDIR := lib
DISABLE_RIBBON := true
INDEX_FORMAT := md
GHPAGES_COMMIT_TTL = 7
GHPAGES_BRANCH_TTL = 2
XML_RESOURCE_ORG_PREFIX := https://xml2rfc-tools-ietf-org.lucaspardue.com/public/rfc


include $(LIBDIR)/main.mk

$(LIBDIR)/main.mk:
ifneq (,$(shell grep "path *= *$(LIBDIR)" .gitmodules 2>/dev/null))
	git submodule sync
	git submodule update $(CLONE_ARGS) --init
else
	git clone -q --depth 10 $(CLONE_ARGS) \
	    -b index-titles https://github.com/martinthomson/i-d-template $(LIBDIR)
endif

$(GHPAGES_EXTRA):
	ln -sf draft-ietf-httpbis-$@ $@

clean::
	-rm -f $(GHPAGES_EXTRA)

lint:: http-lint

rfc-http-validate ?= rfc-http-validate
.SECONDARY: $(drafts_xml)
.PHONY: http-lint
http-lint: $(drafts_xml) http-lint-install
	$(rfc-http-validate) -q -m sf.json $(filter-out http-lint-install,$^)

.PHONY: http-lint-install
http-lint-install:
	@hash $(rfc-http-validate) 2>/dev/null || pip3 install rfc-http-validate typing_extensions
