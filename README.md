# Protect Test
[Sublime Text](http://www.sublimetext.com/) plugin to aid in [Selenium](http://seleniumhq.org/) test breakage detection/prevention/resolution.

## General Strategy
1. By including a _meta_ tag in the HTML file under test, with a _test_ attribute pointing to the path of the selenium test suite, e.g. `<meta test="/path/to/test"/>`, the test file is parsed for test information, for example, the type of test (_e.g. assertElementPresent, clickAndWait, verifyText, etc._), the [XPath](https://en.wikipedia.org/wiki/XPath) locator of the element, etc.
2. From here, the [_EventListener_](https://www.sublimetext.com/docs/3/api_reference.html#sublime_plugin.EventListener) class from the [Sublime Text API](https://www.sublimetext.com/docs/3/api_reference.html) is used. This class provides _asynchronous listeners_ that are triggered on UI actions within Sublime Text, like moving the cursor, making edits, etc. Depending on the test type and which _harmful edits_ could potentially break that test, these listeners will trigger a parse of the code that is being edited. Upon detecting such a _harmful edit_, the user will be notified of the test they are potentially breaking, and potentially given a means of automatically repairing the breakage.

### Missing Value Algorithm
processing_tests: Goes through the list of parsed tests for this file, decides what to look for depending on test type.

getTree : Returns a parse tree for the document. Uses [lxml](http://lxml.de/) to parse the HTML.

test.missingValueSkip: If the link is not a part of a form, the missing value check will not need to be performed, and can be skipped.

originalForm: "Master" copy of the form required attributes, as it was originally, prior to any edits.

buildFormList: This function takes a form element as a parameter. It goes through the children of the element, and if a child has the *required* attribute, generates an XPath selectors for it and adds it to a list. This list is returned after all children have been iterated.

compareForms: This function compares _originalForm_ to _formElement_. If there are differences, this suggests that the use has added an additional *required* attribute which would break the test, and the user is notified.  

```
static originalForm = NULL;

while(processing_tests()) {
    if (test.type == 'clickAndWait'  && !test.missingValueSkip) /*This indicates that the test follows a link */
    {
      tree = getTree();
      try:
      processForm(test.locator, document, test)
      except:
      /*With invalid HTML, an exception will be raised. Skip the check until there is valid HTML.*/
      continue;
    }
}
```

```
function processForm(XPathLocator, parseTree, test) {
  formElement = NULL;
  button = parseTree.getXpath(XPathLocator); /* Select element pointed to by XPath from the parse tree. */
  for each (element in button.ancestors()) {
    if (element.tag == "form") { /*The element is a form element */
      if (originalForm == NULL) { /*Build "master" copy of form required elements */
        originalForm = buildFormList(element);
      } else {
        formElement = buildFormList(element); /*Get copy of required form elements in buffer to compare to master*/
      }
      break;
    }
  }
  if (originalForm == NULL && formElement == NULL) {
    /* Link is not part of a form, cannot suffer from missing value breakage */
    test.missingValueSkip = True;
    return;
  }
  if (formElement != NULL) {
    if (compareForms(formElement)) {
      alertUser;
    }
  }
}
```


#### To install:
###### OSX:
For now, clone this repository and create a symlink to the "Protect Test" folder in the `~/Library/Application Support/Sublime Text 3/Packages` folder. In the future, installation will be automated via [Package Control](https://packagecontrol.io/).


