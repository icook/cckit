import pytest
import base64

from ..networks import Bitcoin
from io import BytesIO


transaction_tests = [
    (
        "AQAAAALcOOk1m9faO1g4YgThhtlAhoX0J/XlE2ZttzWqimshaQAAAABqRzBE"
        "AiBdj+6zEkeORo0LUU5j4ROVjXIU+lcqzYcHmn8MwCb8XAIgD6duoFvyQ69t"
        "D5F38kHK9gbQH8/V5i1r77yiTlaeXCcDIQIQChqcosGJMtZXfFjyJVgBhNDg"
        "gibUGVmHSslj48Gy/v/////cOOk1m9faO1g4YgThhtlAhoX0J/XlE2ZttzWq"
        "imshaQEAAABrSDBFAiAIft44cp5tNeT1FVBQGOZZIiAxJztzZpIPOT7jqxe8"
        "HgIhAMpDFkt1fRptEjXxMgDUtfdt2P2k7J/ChUay31sSEejfAyECdZg5E+YA"
        "k7dn6FWXypOX+y9Bjlf5mNavu8U2EWCFscv/////AUCJlQAAAAAAGXapFPzJ"
        "s204z1XX1bTuTd22ssF2EvSMiKwAAAAA",
        ""
    ),
    (
        "AQAAAAEtUf3HWib/PGE4Ag4am7QPH6tuOc6W/q4yGMmuA14AqwEAAABrSDBF"
        "AiEA5PGlIZB+UPxE0zEy7pjJcVpk350sKGDj4EdMUhq4U34CIDCvjTUGpTUu"
        "KwVkRazYVaQtNycOlKYpp7KLIYcOxtdhASEDgIxJPwYZkNK+AB5A8EiuiHAy"
        "C3SJXOLZZS88HHPNbyz/////AvCHSwAAAAAAGXapFPzJs204z1XX1bTuTd22"
        "ssF2EvSMiKzwh0sAAAAAABl2qRQzzvYXSdEboq3wkaXgRWeBd/46bYisAAAA"
        "AA==",
        ""
    ),
    (
        "AQAAAAJa+fLO2OCiRk98qhSvobvRyPsY3qrl0QEZa1jcIn70rgAAAABqRzBE"
        "AiANKFITbLHEu93eBOx29YHRsyockZFIyF+8D9BWXTWK8wIgNvKqF87Ind6w"
        "A3aigYv3KMRHmSgLnyBExWkad7Dc2WwDIQIQChqcosGJMtZXfFjyJVgBhNDg"
        "gibUGVmHSslj48Gy/v////9a+fLO2OCiRk98qhSvobvRyPsY3qrl0QEZa1jc"
        "In70rgEAAABrSDBFAiEA9APIYMTjztPlIyyzWCXnk3It+vCsLwGWGpN4K0kG"
        "qWMCIGLdifJz5mvPrW8FqLDNJrp7Bma+/Qw9pF2feVcX2lBKAyECdZg5E+YA"
        "k7dn6FWXypOX+y9Bjlf5mNavu8U2EWCFscv/////AaAClAAAAAAAGXapFOUK"
        "XY2jOZUbBAutBFPXxAz9dNPciKwAAAAA",
        ""
    ),
    (
        "AQAAAAGfYeIRrb5mi2ycUPFoaEqbONlRKDXMKYFmaW3C1MdaMQAAAABsSTBG"
        "AiEAhIisrGQ/6Sa7DAJtv+pa9nMiHuBTLNAkxlyzDjYvGEQCIQCFH27K+zjJ"
        "ItZHnrCORpOhrBnHvPnUX8mqXy1pGB/4ngEhAhAKGpyiwYky1ld8WPIlWAGE"
        "0OCCJtQZWYdKyWPjwbL+/////wKgxEoAAAAAABl2qRT8ybNtOM9V19W07k3d"
        "trLBdhL0jIisoMRKAAAAAAAZdqkUM872F0nRG6Kt8JGl4EVngXf+Om2IrAAA"
        "AAA=",
        ""
    ),
    (
        "AQAAAALCBkSoNGHOnUgtcCy8I87ODdMmW1WL56GNNOIWvaccAAAAAABrSDBF"
        "AiAxKffbGKLs4sDhPFwLZvQlHX+Q20uxr0hFzQqtnSQZQAIhAImY0R1z7HrT"
        "Tt4hR0R/3n3eS8LXk14G94/O8Pc7LDlmAyECE2UQ39BTBuo0mCvz395yuOSd"
        "QyqYBb9kUtOZTnkvnRn/////yRF9O6xy+bn8PWf3KNM1uywKHCYWOL0bgEe1"
        "Zd1jGaIAAAAAakcwRAIgRQ7h/BpT6uurhfpEmEE/Xx5OAZdUohj+Euzr3Zg8"
        "mbkCIDxIakZ02TMLAtt5OHKyy0VQw7uywxjyis6540zeNZdJAyED78tvrsro"
        "6386Jta3YJd/I64guTuYS8oof9K4PDGZeHD/////AeD9HAAAAAAAGXapFB0x"
        "6lo758/yr1vtc3EOtvXV9n1wiKwAAAAA",
        ""
    ),
    (
        "AQAAAAKerCh2TFeXmFaXU1qdQUucoCL5WRFVNZdvNt1FZgp5XQAAAACMSTBG"
        "AiEAvLz97Qz/zSlKSDrllLRwj73G2B7RfaiR1ZspOG5Ae3kCIQD5ATZgiNvH"
        "X8Tn8Ib8RohgW0HGbPRi00XUcvxCTmybGgFBBCsXId9LDBz91gENMCmVXxRE"
        "ZI+E6QOSkToVTtny7tiOJhmHy/jci4KzQmucvUBotsK5r4CiwjhjOkAAXRD6"
        "SWD/////6864dM1/4fxjvltUc0HJ1da9agsSw4LV3KYhGR7FJ+MBAAAAi0gw"
        "RQIhAJIopjUy7dPOHa+LGTvgM4jfZ8pA522/Jx3+uFC4Lz5IAiBzLNoxejaa"
        "dw1CXwOUuzI4rMl0xsuYC5XQaxZNT2TFzwFBBBPpriULEjb9VdVoC8v3E4is"
        "RMmfQByPCJYadSwK/ZZg9TTFGyDXUwW+dQ9tScDzhMWfdLK9DyV4iAbnYh/S"
        "2cr/////A0BCDwAAAAAAGXapFFzGycfh13x6rrUPhNJNj2ViE7xbiKwACT0A"
        "AAAAABl2qRQhQVEH8cwnc3//rGPcfvakBANJxIistBcsAAAAAAAZdqkUMQV+"
        "QpfDgBAsCQ+ixaUK5Kgl0kOIrAAAAAA=",
        ""
    ),
    (
        "AQAAAAO1CFlm1mEB3fjCtilQEH+6TbR3UzdJyqafj3mab9Mc6gAAAACKRzBE"
        "AiA8rWZ4BB8YYJp3xtx8jAZdrfQ6B0zjYRdgTS7I5LZF7gIgabCjn9iu9L3n"
        "YvKrdXFJJygtbg6V8iMTLrPh8ghdGvwBQQQrFyHfSwwc/dYBDTAplV8URGSP"
        "hOkDkpE6FU7Z8u7YjiYZh8v43IuCs0JrnL1AaLbCua+AosI4YzpAAF0Q+klg"
        "/////8IGRKg0Yc6dSC1wLLwjzs4N0yZbVYvnoY004ha9pxwAAQAAAItIMEUC"
        "IDNZYWLuCV0nJL6CCGgUfQfNoh0oAACd2lMZn+zJdJCDAiEAqZafa18G1K1x"
        "/6yOvj8h1uAGSM8UjSJJ6479li5sos4BQQTswrqYR5m+x0vFTzgGrrM2k+Gx"
        "gX+hDBAvN8Kq9RRuWdqC4jVNGhGdFD63Ev1TQYXMqvp6b9ztbAZ3ED8i6sFo"
        "/////0Vf19DzvUs2DvFwlVW9viTF+YlXCNYNMD6yUXK9I9RBAgAAAItIMEUC"
        "IQCKbaQY2eH1fsXZFksstrP4B+uxPBwGRe2Wxl7rW5sYGwIgVvVEPdnJNvVj"
        "rh0XZdhqnOAA0Sw39Upqkejrm+yXWnwBQQQ1hDJBuzoTc1ZJ8zyVQjEfRcjW"
        "o8rq3lE+3x3rYZ3Q/9xBEBtsnkFAzps/N8n6C5cK2QAmRGxeGFmbYaGFT5RP"
        "/////wNAQg8AAAAAABl2qRSU70Qwi2d2bI+nKnCP19XGsbSnWoisVEkwAAAA"
        "AAAZdqkUgroT7ai54LzKPXVnWJsPoV6lJ0yIrHjrFQAAAAAAGXapFEFyZV9I"
        "izJXnWmTivO2n9OKDWCdiKwAAAAA",
        ""
    ),
    (
        "AQAAAAHBHumhtHyFj2ma501AFchO/RrrfkY1sYTKsJiYe6i5pAEAAADaAEcw"
        "RAIgJQsMj5xe4yyGSQOseNBu7zuQNbdwYRpmu4tyOeVrDhoCIHTRJ5lHr5OH"
        "JsmDYl4nTEMhT2TeEN8tMNtrt/rFLMaHAUgwRQIhAObKZ2o5NubR2aoXKP7q"
        "oNMI3sv4u33Hnxcu1NBCilhoAiAH5OaEGAC5snVQDIWgXXVWICosFmTHHjXg"
        "y5fNwAO5gAFHUiECzr9qtYCUjRRrfMdx2OZGl0NJ09exHz4DKH0Jl6R307kh"
        "A3umUUhbeiyyIhketkpVkm5iu6v+m17SqUiKrVR7IEKCUq7/////An1KDwAA"
        "AAAAGXapFNxnIa33YyARGtMFwzhMdn1LmeGViKxllyYPAAAAABepFNsSg3N8"
        "2T68HrEpjWRKeEbFWm2WhwAAAAA=",
        ""
    ),
    (
        "AQAAAAHZI2Rm7Gvz7UMEKi20P7AIT5AOxlhwW29S0uFz9EPz1QEAAADaAEgw"
        "RQIhAIX1NZuYzrKUHFAxUNYI6yWMUuzCEapuZOUY6TdCspWaAiAchzgPP6if"
        "WNh0cmVkyW1UpygM/eVa1XrtHepCMhvArAFHMEQCIGLJtKtbyJEaH6iQS+hK"
        "xUlGrWwmqdJScz/JfSZ1Qln6AiBNRC+gswEEMjTNR5uVetqCGJkNL2m6fDfk"
        "DyICU/otoQFHUiECzr9qtYCUjRRrfMdx2OZGl0NJ09exHz4DKH0Jl6R307kh"
        "A3umUUhbeiyyIhketkpVkm5iu6v+m17SqUiKrVR7IEKCUq7/////Aux5CAAA"
        "AAAAGXapFDIKbLrYWAn/2ZTB7ToisbIaZ5DoiKzL5TUPAAAAABepFNsSg3N8"
        "2T68HrEpjWRKeEbFWm2WhwAAAAA=",
        ""
    ),
    (
        "AQAAAAGsp/O0VlTCMOCIalf7mIwwRO9ej385cm0wXGHV6BiQPAAAAAD9XQEAS"
        "DBFAiABh6+Sjp0VXEsaycHJEYFTI5q6dndPd118H5w+EG/zPAIhAIgisPZY7e"
        "wiJ00LauneEOvy2gaxu9qrpOUOsHjznj14AUcwRAIgeV8PT1lBp3rgMuy54zd"
        "TeI1+tcsMeNgFV11rAKHZv+0CID4fStkzLRQWrgHicDjpRbydtZxzJyijg6bx"
        "7S+5naekAUzJUkEEkbuiUQkSpb032h+1sWcwEOQ9LG2BLFFOkb+p8usSnhwYM"
        "ynbVb2GjiCarC+8Assz2Y/nS/I/DCNdYSax2DNPhkEEhlxAKTpoDLnAIOex4Q"
        "bYwZFtPO+ZqkMaVtJT5pJW2sCe8SKxqYaBiny2JFMvBiwdH4ciCEhhxcMpHM/"
        "+9OxodEEEjSRV0kA+CHCPwfVWAC8bbNg/mS0IUJf5l0qwiiiDjweJb7qwjzlJ"
        "XhX6b61u2/sedU41+hx4RMQfMioYY9RiE1Ou/////wFAQg8AAAAAABl2qRSuV"
        "rTbE1VNMhxALbOWEYeu0bvtW4isAAAAAA==",
        ""
    ),
    (
        "AQAAAAGJYyhI+ZcikVcnxcddqNstvxlDQqBCmCj2b/iPqyr31gAAAACLSDBFA"
        "iEAq7yKc/4gVEgL2j8ygdotDFHihBORq9TAn0+QiiA0wY0CIFvJ5NaOr7kY8+"
        "lmIzhkekQZwN4aZQq4mD8dIW4qMdjjAUEEb1XXre/2ARx+rClP5UDFeDC+gOk"
        "1XIOGnJJgpLi/R2ema6y9cLgE3GPVvusUGAKSrX87CDNysdAtejfdl/9cnv//"
        "//8BQEIPAAAAAAAXqRT4FbA22bu85enyoAq9G/PckelVEIcAAAAA",
        ""
    )
]


@pytest.mark.parametrize("b64tx,hash", transaction_tests)
def test_transaction_recode(b64tx, hash):
    tx_bytes = base64.b64decode(b64tx)
    stream = BytesIO(tx_bytes)
    tx = Bitcoin.transaction.from_network(stream)
    stream2 = BytesIO(tx_bytes)
    tx.to_network(stream2)
    stream2.seek(0)
    assert stream2.read() == tx_bytes
