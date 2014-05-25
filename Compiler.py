
# Jack to VM compiler Python program
# by pikapike

# import compiler-related stuff

import collections
import re

# a named tuple (mainly for testing)
Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column', 'token_number'])

# the Tokenizer (still those pesky comments)
class JackTokenizer:
    def __init__(self, file):
        self.file = open(file, "r")
        self.file.seek(0, 0)
        self.filestring = self.file.read()
        self.file.seek(0, 0)
        self.token_number = -1
        self.tokens = []
        self.token = None
        self.i = 0
    def somefunction(self, something):
        try:
            if self.filestring[self.i]+self.filestring[self.i+1] == something:
                return True
            else:
                return False
        except:
            return False
    def antiComment(self):
        multlinestr = ''
        linecomment = False
        multilinecomment = False
        self.i = 0
        while self.i < len(self.filestring):
            if linecomment == True:
                if (self.filestring[self.i] == '\r'):
                    linecomment = False
            elif multilinecomment == True:
                if self.somefunction("*/"):
                    multilinecomment = False
                    self.i += 1
            elif self.somefunction("//"):
                linecomment = True
            elif self.somefunction("/*"):
                multilinecomment = True
            else:
                multlinestr += self.filestring[self.i]
            self.i += 1
        self.filestring = multlinestr.rstrip()
    def tokenize(self):
        keywords = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}
        token_specification = [
	    ('SYMBOL', r'[\{\}\(\)\[\].,;\+\-\*\/&|<>=~]'), # Jack symbols
	    ('INT_CONST', r'\d+(\.\d*)?'), # Jack decimal numbers (warning: no test for up to 32767)
          ('IDENTIFIER', r'[A-Za-z_][A-Za-z0-9_]*'),   # Identifiers
          ('NEWLINE', r'[\n\r]'),          # Line endings
        ('SKIP',    r'[ \t]'),       # Skip over spaces and tabs
        ('STRING_CONST', r'\"[^\n\"]*?\"') # Strings
	    ] 
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        get_token = re.compile(tok_regex).match
        token_number = 0
        line = 1
        pos = line_start = 0
        mo = get_token(self.filestring)
        val = ''
        while mo is not None:
            typ = mo.lastgroup
            if True:
                if typ == 'NEWLINE':
                    line_start = pos
                    line += 1
                elif typ != 'SKIP':
                    val = mo.group(typ)
                    if typ == 'IDENTIFIER' and val in keywords:
                        typ = 'KEYWORD'
                yield Token(typ, val, line, mo.start()-line_start, token_number)
            token_number += 1
            pos = mo.end()
            mo = get_token(self.filestring, pos)
        if pos != len(self.filestring):
            raise RuntimeError('Unexpected character %r on line %d' %(line))
    def generateTokens(self):
        for token in self.tokenize():
    		self.tokens.append(token)
    def printTokens(self):
        for token in self.tokenize():
            print token
    def advance(self):
        try:
            self.token_number += 1
            self.token = self.tokens[self.token_number]
            return True
        except:
            return False
    def tokenType(self):
        return self.token.typ
    def symbol(self):
        return self.token[1]
    def identifier(self):
        return self.token[1]
    def intVal(self):
        return int(self.token[1])
    def stringVal(self):
        return str(self.token[1])

class CompilationEngine:
    def __init__(self, tokenlist, outputfile):
        self.tokenlist = tokenlist
        self.outfile = outputfile
        self.token_number = 0
        self.ops = ('+', '-', '*', '/', '&', '|', '<', '>', '=')
        self.unaryOps = ('-', '~')
        self.keywordConstants = ('true', 'false', 'null', 'this')
    def useToken(self):
        while (self.tokenlist[self.token_number][0] == 'NEWLINE') or (self.tokenlist[self.token_number][0] == 'SKIP'):
            self.token_number += 1
            print "skip!"
        token = (self.tokenlist[self.token_number][1], 0)
        print token[0], self.token_number
        self.token_number += 1
        return token[0]
    def indicateToken(self):
        while (self.tokenlist[self.token_number][0] == 'NEWLINE') or (self.tokenlist[self.token_number][0] == 'SKIP'):
            self.token_number += 1
            print "skip!"
        print self.tokenlist[self.token_number][1]
        return self.tokenlist[self.token_number][1]
    def getTokenType(self):
        return self.tokenlist[self.token_number][0]
    def boolToken(self, string):
        print  self.indicateToken()     
        return self.indicateToken() == string
    def compileType(self):
        if self.getTokenType() == 'IDENTIFIER':
            return '<identifier> ' + self.useToken() + ''' </identifier>
            '''
        else:
            return '<keyword> ' + self.useToken() + ''' </keyword>
            '''
    def compileClass(self):
        xmlstr = '''<class>
        <keyword> ''' + self.useToken() + ''' </keyword>
        <identifier> ''' + self.useToken() + '''</identifier>
        <symbol> '''+ self.useToken() + ''' </symbol>
        '''
        print self.token_number
        while self.indicateToken() != '}':
            print "I know you're endless looping!!!"
            if (self.boolToken('constructor')) or (self.boolToken('function')) or (self.boolToken('method')):
                xmlstr += self.compileSubroutine()
            elif (self.boolToken('field')) or (self.boolToken('static')):
                xmlstr += self.compileClassVarDec()
            else:
                print 1 % 0
        xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
        </class>
        '''
        return xmlstr
    def compileClassVarDec(self):
        xmlstr = '''<classVarDec>
        <keyword> ''' + self.useToken() + ''' </keyword>
        ''' + self.compileType() + '<identifier> ' + self.useToken() + ''' </identifier>
        '''
        while self.indicateToken() != ';':
            print "Cuckoo!"
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            <identifier> ''' + self.useToken() + ''' </identifier>
            '''
        xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
        </classVarDec>
        '''
        return xmlstr
    def compileSubroutine(self):
        xmlstr = '''<subroutineDec>
        <keyword> ''' + self.useToken() + ''' </keyword>
        '''
        if self.indicateToken() == 'void':
            xmlstr += '<keyword> ' + self.useToken() + ''' </keyword>
        '''
        else:
            xmlstr += self.compileType()
        xmlstr += '<identifier> ' + self.useToken() + '''</identifier>
        <symbol> ''' + self.useToken() + ''' </symbol>
        ''' + self.compileParameterList() + '<symbol> ' + self.useToken() + ''' </symbol>
        <subroutineBody>
        <symbol> ''' + self.useToken() + ''' </symbol>
        ''' + self.compileVarDec() + self.compileStatements() + '''<symbol> ''' + self.useToken() + ''' </symbol>
        </subroutineDec>
        '''
        return xmlstr
    def compileParameterList(self):
        xmlstr = '''<parameterList>
        '''
        if self.indicateToken() != ')':
            xmlstr += self.compileType() + '<identifier> ' + self.useToken() + '''</identifier>
            '''
        while self.indicateToken() != ')':
            print "Woohoo!"
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileType() + '<identifier> '  + self.useToken() + '''</identifier>
            '''
        xmlstr += '''</parameterList>
        '''
        return xmlstr
    def compileVarDec(self):
        xmlstr = '''<varDec>
        <keyword> ''' + self.useToken() + ''' </keyword>
        ''' + self.compileType() + '<identifier> ' + self.useToken() + ''' </identifier>
        '''
        while self.indicateToken() != ';':
            print "Doops?"
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            <identifier> ''' + self.useToken() + ''' </identifier>
            '''
        xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
        </varDec>
        '''
        return xmlstr
    def compileStatements(self):
        xmlstr = '''<statements>
        '''
        while self.indicateToken() != '}':
            print self.token_number, self.indicateToken()
            if self.indicateToken() == 'let':
                xmlstr += self.compileLet()
            elif self.indicateToken() == 'if':
                xmlstr += self.compileIf()
            elif self.indicateToken() == 'while':
                xmlstr += self.compileWhile()
            elif self.indicateToken() == 'do':
                xmlstr += self.compileDo()
            elif self.indicateToken() == 'return':
                xmlstr += self.compileReturn()
        xmlstr += '''</statements>
        '''
        return xmlstr
    def compileDo(self):
        xmlstr = '''<doStatement>
        <keyword> ''' + self.useToken() + '''</keyword>
        ''' + self.compileTerm() + '<symbol> ' + self.useToken() + ''' </symbol>
        </doStatement>
        '''
        return xmlstr
    def compileLet(self):
        xmlstr = '''<letStatement>
        <keyword> ''' + self.useToken() + ''' </keyword>
        <identifier> ''' + self.useToken() + ''' </identifier>
        '''
        print self.indicateToken()
        if self.indicateToken() != '=':
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
            '''
        xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
        ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
        </letStatement>
        '''
        return xmlstr
    def compileWhile(self):
        xmlstr = '''<whileStatement>
        <keyword> ''' + self.useToken() + ''' </keyword>
        <symbol> ''' + self.useToken() + ''' </symbol>
        ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
        <symbol> ''' + self.useToken() + ''' </symbol
        ''' + self.compileStatements() + '<symbol> ' + self.useToken() + ''' </symbol>
        </whileStatement>
        '''
        return xmlstr
    def compileReturn(self):
        xmlstr = '''<returnStatement>
        <keyword> ''' + self.useToken() + ''' </keyword>
        <symbol> ''' + self.useToken() + ''' </symbol>
        '''
        if self.indicateToken() != ';':
            self.compileExpression()
        xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
        </returnStatement>'''
        return xmlstr
    def compileIf(self):
        xmlstr = '''<ifStatement>
        <keyword> ''' + self.useToken() + ''' </keyword>
        <symbol> ''' + self.useToken() + ''' </symbol>
        ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
        <symbol> ''' + self.useToken() + ''' </symbol>
        ''' + self.compileStatements() + '<symbol> ' + self.useToken() + ''' </symbol>
        '''
        if self.indicateToken() == 'else':
            xmlstr += '<keyword> ' + self.useToken() + ''' </keyword>
            <symbol> ''' + self.useToken() + ''' </symbol>
            ''' + self.compileStatements() + '<symbol> ' + self.useToken() + ''' </symbol>
            <symbol> ''' + self.useToken() + ''' </symbol>
            '''
        xmlstr += '''</ifStatement>
        '''
        return xmlstr
    def compileExpression(self):
        xmlstr = '''<expression>
        ''' + self.compileTerm()
        while self.indicateToken() in self.ops:
            print "o_0"
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileTerm()
        xmlstr += '''</expression>
        '''
        return xmlstr
    def compileTerm(self):
        xmlstr = '''<term>
        '''
        if self.getTokenType() == 'INT_CONST':
            xmlstr += '<integerConstant> ' + self.useToken() + ''' </integerConstant>
            '''
        elif self.getTokenType() == 'STRING_CONST':
            xmlstr += '<stringConstant> ' + self.useToken() + ''' </stringConstant>
            '''
        elif self.indicateToken() in self.keywordConstants:
            xmlstr += '<keyword> ' + self.useToken() + ''' </keyword>
            '''
        elif self.getTokenType() == 'IDENTIFIER':
            xmlstr += '<identifier> ' + self.useToken() + ''' </identifier>
            '''
            if self.indicateToken() == '[':
                xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
                ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
                '''
            elif self.indicateToken() == '(':
                xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
                ''' + self.compileExpressionList() + '<symbol> ' + self.useToken() + ''' </symbol>
                '''
            elif self.indicateToken() == '.':
                xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
                <identifier> ''' + self.useToken() + ''' </identifier>
                <symbol ''' + self.useToken() + ''' </symbol>
                ''' + self.compileExpressionList() + '<symbol> ' + self.useToken() + ''' </symbol>
                '''
        elif self.indicateToken() == '(':
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileExpression() + '<symbol> ' + self.useToken() + ''' </symbol>
            '''
        elif self.indicateToken() in self.unaryOps:
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileTerm()
        xmlstr += '''</term>
        '''
        return xmlstr
    def compileExpressionList(self):
        xmlstr = '''<parameterList>
        '''
        if self.indicateToken() != ')':
            xmlstr += self.compileExpression()
        while self.indicateToken() != ')':
            print ["l", "i", "s", "t"]
            xmlstr += '<symbol> ' + self.useToken() + ''' </symbol>
            ''' + self.compileExpression()
        xmlstr += '''</parameterList>
        '''
        return xmlstr

def tokenize(file):
    print "StartTest"
    tokenizer = JackTokenizer(file)
    print "TEST0"
    tokenizer.antiComment()
    print "TEST1"
    tokenizer.printTokens()
    tokenizer.generateTokens()
    advancing = True
    tokenizer.advance()
    print "TEST2"
    while advancing:
        if tokenizer.tokenType() == 'KEYWORD':
            print tokenizer.symbol()
        if tokenizer.tokenType() == 'SYMBOL':
            print tokenizer.symbol()
        if tokenizer.tokenType() == 'INT_CONST':
            print tokenizer.intVal()
        if tokenizer.tokenType() == 'IDENTIFIER':
            print tokenizer.identifier()
        if tokenizer.tokenType() == 'STRING_CONST':
            print tokenizer.stringVal()
        advancing = tokenizer.advance()
    compilation = CompilationEngine(tokenizer.tokens, "asdf")
    print compilation.compileClass()
    
print "Hello! We are sdalfkjsdlfsad"    
tokenize("Square.jack")
tokenize("SquareGame.jack")
tokenize("Main.jack") 

