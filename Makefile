xml2rfc ?= "xml2rfc"
saxpath ?= "lib/saxon9.jar"
saxon ?= java -classpath $(saxpath) net.sf.saxon.Transform -l
kramdown2629 ?= XML_RESOURCE_ORG_PREFIX=https://xml2rfc.tools.ietf.org/public/rfc kramdown-rfc2629

names := rfc6265bis key client-hints origin-frame cache-digest header-structure expect-ct early-hints rand-access-live replay http2-secondary-certs
drafts := $(addprefix draft-ietf-httpbis-,$(names))
last_tag = $(shell git tag | grep "$(draft)" | sort | tail -1 | awk -F- '{print $$NF}')
next_ver = $(if $(last_tag),$(shell printf "%.2d" $$(( 1$(last_tag) - 99)) ),00)
next := $(foreach draft, $(drafts), $(draft)-$(next_ver))

TARGETS := $(addsuffix .txt,$(drafts)) \
	  $(addsuffix .html,$(drafts))
friendly_names := rfc6265bis key client-hints origin-frame cache-digest header-structure expect-ct early-hints rand-access-live replay secondary-certs
FRIENDLY := $(addsuffix .txt,$(friendly_names)) \
	    $(addsuffix .html,$(friendly_names))

.PHONY: latest submit idnits clean issues.json $(names)
.INTERMEDIATE: $(addsuffix .redxml,$(drafts))
.PRECIOUS: $(TARGETS)

latest: $(TARGETS)

# build rules for specific targets
makerule = $(join $(addsuffix :: ,$(names)),$(addsuffix .$(1),$(drafts)))
$(foreach rule,$(call makerule,txt) $(call makerule,html),$(eval $(rule)))

submit: $(addsuffix .txt,$(next))

idnits: $(addsuffix .txt,$(next))
	idnits $<

clean:
	-rm -f $(addsuffix .redxml,$(drafts))
	-rm -f $(addsuffix *.txt,$(drafts))
	-rm -f $(addsuffix *-[0-9][0-9].xml,$(drafts))
	-rm -f $(addsuffix *.html,$(drafts))

rfc6265bis.%: draft-ietf-httpbis-rfc6265bis.%
	cp -f $< $@

key.%: draft-ietf-httpbis-key.%
	cp -f $< $@

client-hints.%: draft-ietf-httpbis-client-hints.%
	cp -f $< $@

origin-frame.%: draft-ietf-httpbis-origin-frame.%
	cp -f $< $@

cache-digest.%: draft-ietf-httpbis-cache-digest.%
	cp -f $< $@

header-structure.%: draft-ietf-httpbis-header-structure.%
	cp -f $< $@

expect-ct.%: draft-ietf-httpbis-expect-ct.%
	cp -f $< $@

early-hints.%: draft-ietf-httpbis-early-hints.%
	cp -f $< $@

rand-access-live.%: draft-ietf-httpbis-rand-access-live.%
	cp -f $< $@

replay.%: draft-ietf-httpbis-replay.%
	cp -f $< $@

secondary-certs.%: draft-ietf-httpbis-http2-secondary-certs.%
	cp -f $< $@

define makerule_submit_xml =
$(1)
	sed -e"s/$$(basename $$<)-latest/$$(basename $$@)/" $$< > $$@
endef
submit_deps := $(join $(addsuffix .xml: ,$(next)),$(addsuffix .redxml,$(drafts)))
$(foreach rule,$(submit_deps),$(eval $(call makerule_submit_xml,$(rule))))

%.xml: %.md
	$(kramdown2629) $< | sed -e 's/\"rfc2629.dtd\"/\"lib\/rfc2629.dtd\"/' > $@

$(addsuffix .txt,$(next)): %.txt: %.xml
	$(xml2rfc) $< $@

%.txt: %.redxml
	$(xml2rfc) $< $@

stylesheet := lib/rfcbootstrap.xslt
%.html: %.xml $(stylesheet) $(extra_css)
	$(saxon) $< $(stylesheet) > $@

reduction := lib/clean-for-DTD.xslt
%.redxml: %.xml $(reduction)
	$(saxon) $< $(reduction) > $@

%.xhtml: %.xml ../../rfc2629xslt/rfc2629toXHTML.xslt
	$(saxon) $< ../../rfc2629xslt/rfc2629toXHTML.xslt > $@

GHPAGES_TMP := /tmp/ghpages$(shell echo $$$$)
.TRANSIENT: $(GHPAGES_TMP)
ifeq (,$(TRAVIS_COMMIT))
GIT_ORIG := $(shell git branch | grep '*' | cut -c 3-)
else
GIT_ORIG := $(TRAVIS_COMMIT)
endif

IS_LOCAL := $(if $(TRAVIS),true,)
ifeq (master,$(TRAVIS_BRANCH))
IS_MASTER := $(findstring false,$(TRAVIS_PULL_REQUEST))
else
IS_MASTER := true
endif

ghpages: $(FRIENDLY) $(TARGETS)
ifneq (,$(or $(IS_LOCAL),$(IS_MASTER)))
	mkdir $(GHPAGES_TMP)
	cp -f $^ $(GHPAGES_TMP)
	git clean -qfdX
ifeq (true,$(TRAVIS))
	git config user.email "ci-bot@example.com"
	git config user.name "Travis CI Builder"
	git checkout -q --orphan gh-pages
	git rm -qr --cached .
	git clean -qfd
	git pull -qf origin gh-pages --depth=5
else
	git checkout gh-pages
	git pull
endif
	mv -f $(GHPAGES_TMP)/* $(CURDIR)
	git add $^
	if test `git status -s | wc -l` -gt 0; then git commit -m "Script updating gh-pages."; fi
ifneq (,$(GH_TOKEN))
	@echo git push -q https://github.com/$(TRAVIS_REPO_SLUG).git gh-pages
	@git push -q https://$(GH_TOKEN)@github.com/$(TRAVIS_REPO_SLUG).git gh-pages >/dev/null 2>&1
endif
	-git checkout -qf "$(GIT_ORIG)"
	-rm -rf $(GHPAGES_TMP)
endif

# backup issues
issues.json:
	python lib/fetch-issues.py > issues.json
