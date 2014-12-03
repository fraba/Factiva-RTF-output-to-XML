# Python script to translate Factiva .rtf output into a structured XML document

The script does exactly this. It will produce an XML document with this schema

```
<?xml version="1.0" encoding="UTF-8" ?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:complexType name="article">
    <xs:sequence>
        <xs:element name="title" type="xs:string"/>
	<xs:element name="words" type="xs:positiveInteger"/>
	<xs:element name="publication" type="xs:string"/>
	<xs:element name="publication_id" type="xs:string"/>
	<xs:element name="page" type="xs:positiveInteger"/>
	<xs:element name="language" type="xs:string"/>
	<xs:element name="copyright" type="xs:string"/>
	<xs:element name="body" type="xs:string"/>
	<xs:element name="factiva_id" type="xs:string"/>
    </xs:sequence>
  </xs:complexType> 
  </xs:schema>
  ```
