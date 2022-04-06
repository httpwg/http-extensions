# TAG Security & Privacy Questionnaire Answers for *Cookie Expires/Max-Age attribute upper limit* #

* **Author:** arichiv@chromium.org
* **Questionnaire Source:** https://www.w3.org/TR/security-privacy-questionnaire/#questions

## Questions ##

**1. What information might this feature expose to Web sites or other parties, and for what purposes is that exposure necessary?**

N/A, this feature exposes no new information to websites or other parties.

**2. Do features in your specification expose the minimum amount of information necessary to enable their intended uses?**

Yes, no new information is exposed.

**3. How do the features in your specification deal with personal information, personally-identifiable information (PII), or information derived from them?**

It does not deal directly in PII, but websites could be using cookies to store PII.

**4. How do the features in your specification deal with sensitive information?**

It does not handle sensitive information.

**5. Do the features in your specification introduce new state for an origin that persists across browsing sessions?**

No, this specification does not introduce new state (the expiration date was already tracked).

**6. Do the features in your specification expose information about the underlying platform to origins?**

No, the expiration date is not visible to websites.

**7. Does this specification allow an origin to send data to the underlying platform?**

Yes, but no more than the existing cookies spec does.

**8. Do features in this specification enable access to device sensors?**

No
**9. What data do the features in this specification expose to an origin? Please also document what data is identical to data exposed by other features, in the same or different contexts.**

See the answer to question 6.

**10. Do features in this specification enable new script execution/loading mechanisms?**

No

**11. Do features in this specification allow an origin to access other devices?**

No

**12. Do features in this specification allow an origin some measure of control over a user agent’s native UI?**

No

**13. What temporary identifiers do the features in this specification create or expose to the web?**

Nothing beyond what's currently possible with Cookies.

**14. How does this specification distinguish between behavior in first-party and third-party contexts?**

It does not distinguish between them except for the ways that the Cookies spec already does.

**15. How do the features in this specification work in the context of a browser’s Private Browsing or Incognito mode?**

It will work the same, the expiration date limit is enforced there too.

**16. Does this specification have both "Security Considerations" and "Privacy Considerations" sections?**

Yes. https://httpwg.org/http-extensions/draft-ietf-httpbis-rfc6265bis.html#name-privacy-considerations

**17. Do features in your specification enable origins to downgrade default security protections?**

No

**18. How does your feature handle non-"fully active" documents?**

N/A

**19. What should this questionnaire have asked?**

N/A
