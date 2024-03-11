# Python Documentation Style Guide

This document outlines the conventions for writing docstrings in Python code to
ensure consistency and clarity throughout the codebase.

Project documentation should be consistent, logical, and clearly describe the code visually and content-wise.

Use this docstring hierarchy for code documentation:
- [File Level](#file-level-docstrings)
- [Class Level](#class-level-docstrings)
- [Attribute & Constant Level](#attributes-and-constants)
- [Method Level](#method-level-docstrings)

Our docstrings follow a customized
[pep-257](https://www.python.org/dev/peps/pep-0257/) style with added markdown.
For a primer or refresh on our approach, see [Docstrings
101](docstrings_101.md).

## File Level

File-Level docstrings should provide a high-level overview of the file's purpose and contents. This includes a description of the module and its functionality, with a focus on clarity and conciseness. The overview should logically and professionally guide the reader through the file's purpose, highlighting key components and providing relevant examples.

The following sections should be included in File-Level docstrings. This table outlines the required sections, their formatting, and their descriptions.

| Name           | Format         | Description                        |
| -------------- | -------------- | ---------------------------------- |
| Title          | `# Title`      | High-level plain English module name. <br> Example:&nbsp;&nbsp;&nbsp;`MIME Type Agent` |
| Description    | `Plain Text`   | A brief yet thorough overview detailing the module's purpose. |
| Contents       | `List/Table`   | An enumeration of the file's contents, including classes, methods, and variables. |
| Examples       | `Code Blocks`  | At least three examples demonstrating how to use the module, enclosed in triple backticks. |

Examples should be project-relevant and showcase typical usage scenarios. Code blocks should be formatted in Python syntax and be executable to ensure accuracy.


### Examples

Provide generic examples of how to document at the file level using literal markdown syntax. Examples should illustrate the standard docstring format, including a brief module description, a list of contents, and usage examples.

#### File Level Documentation:

```markdown
    # Module Name
    A brief description of the module's purpose.

    ## Contents
    - `Class1`: Description of the first class.
    - `function1`: Description of the first function.

    ## Usage Examples
    ```python
    # Example of using Class1
    class1_instance = Class1()
    ```
```
## Class Level

Class Level docstrings detail the class purpose, scope, and functionality. Include main methods with brief descriptions and a class usage example.

The following sections should be included in Class Level docstrings. This table covers the required sections, their formatting, and their descriptions.

| Name        | Format          | Description                        | Not |
| ----------- | --------------- | ---------------------------------- |-----|
| Class Name  | `# Class Name`  | Plain English class name. <br> Example:&nbsp;&nbsp;&nbsp;`MIME Type Agent` | A literal copy of the class name. <br> Example:&nbsp;&nbsp;&nbsp;`mime_type_agent` |
| Overview    | `Plain Text`    | Overview of the class's purpose and functionality.<br>Use lists, links, and tables where possible. | A dump of all the methods and variables in the class.|
| Attributes  | `Table`         | A table with `Attribute`, `Type`, and `Description` columns. <br>Attribute names must be surrounded by single backticks.<br>Descriptions should clearly describe the attribute's purpose and type. | |
| Constants   | `Table`         | A table with `Constant`, `Type`, and `Description` columns. <br>Constant names should be in uppercase and surrounded by single backticks.<br>Descriptions should indicate the constant's value and its unchanging nature. | |
| Methods     | `Table`         | A table with `Method` and `Description` columns. <br>Method names must be surrounded by single backticks.<br>Descriptions must be a clear, one-sentence description. | |
| Examples    | `## Heading`<br>`Plain Text`<br>`Code Snippets` | Provide at least one, but ideally three simple examples of how to use the class. Be sure to surround code samples in triple backticks. | |

Example for documenting an attribute:

```
| Attribute     | Type        | Description                         |
| ------------- | ----------- | ----------------------------------- |
| `file_path`   | `str`       | Path to the file being processed.   |
```

Example for documenting a constant:

```
| Constant      | Type        | Description                         |
| ------------- | ----------- | ----------------------------------- |
| `MAX_SIZE`    | `int`       | The maximum size allowed in bytes.  |
```

Example for documenting methods:

```
| Method            | Description                              |
| ----------------- | ---------------------------------------- |
| `save_file()`     | Saves the file to the specified path.    |
```

Provide usage examples with complete code snippets:

### Usage Examples

Using the `MIMETypeAgent`:

```python
mime_agent = MIMETypeAgent()
print(mime_agent.detect('file.txt'))
```

## Attributes and Constants

When documenting class attributes and constants, include a table with the name, type, and description. Make sure to specify whether the documented item is an attribute or a constant. Constants should be in uppercase to distinguish them from attributes. Provide any necessary context or usage notes.

### Attributes

Attributes are variables that belong to a class. They can be instance-level or class-level. Document class-level attributes in the class docstring.

Example:

```
| Attribute     | Type        | Description                           |
| ------------- | ----------- | ------------------------------------- |
| `default_rate` | `float`    | The default rate for transactions.    |
```

### Constants

Constants are class-level attributes that should not change once set. By convention, constant names are written in uppercase.

Example:

```
| Constant      | Type        | Description                          |
| ------------- | ----------- | ------------------------------------ |
| `MAX_LIMIT`   | `int`       | The maximum limit for transactions.  |
```

In both cases, provide clear, concise descriptions and the expected type. For constants, also include the constant value if applicable.

## Method Level

Method Level docstrings should provide a clear explanation of the method's functionality, its arguments, return values, and any exceptions it may raise. Document instance methods within the instance method itself and class methods within the class method.

### Description

Start with a brief description of what the method does. Use active voice and present tense.

Example:

```
# `calculate_interest`
Calculates the interest on the principal over a period at a fixed rate.
```

### Arguments

List each argument, its type, and a short description. Include defaults for optional arguments.

Example:

```
| Argument     | Type        | Default | Description                        |
| ------------ | ----------- | ------- | ---------------------------------- |
| `principal`  | `float`     |         | The principal amount.              |
| `rate`       | `float`     | `0.05`  | The interest rate as a decimal.    |
| `time`       | `int`       | `1`     | The time period in years.          |
```

### Returns

Describe the return value and type.

Example:

```
# Returns
The calculated interest as a float.
```

### Raises

List any exceptions that the method explicitly raises.

Example:

```
# Raises
- `ValueError`: If `principal` is less than 0.
```

### Usage Examples

Provide a code example showing how to use the method. Ensure the example is valid Python code and demonstrates typical usage.

Example:

```python
# Example of using `calculate_interest`
interest = calculate_interest(principal=1000, rate=0.05, time=2)
print(interest)  # Output: 100.0
```
