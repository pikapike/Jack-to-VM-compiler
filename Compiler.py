
# Jack to VM compiler Python program
# by Isaac Li

# import compiler-related stuff

import collections
import re

# a named tuple (mainly for testing)
Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column', 'token_number'])

# the Tokenizer
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
	    ('SYMBOL', r'[\{\}\(\)\[\]\.\,\;\+\-\*\/\&\|\<\>\=\~]'), # Jack symbols
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
        return self.token[0]
    def symbol(self):
        return self.token[1]
    def identifier(self):
        return self.token[1]
    def intVal(self):
        return int(self.token[1])
    def stringVal(self):
        return str(self.token[1])

class CompilationEngine:
    def __init__(self, tokenlist, outputfile, symbol_table):
        self.tokenlist = tokenlist
        print len(self.tokenlist)
        self.outfile = outputfile
        self.token_number = 0
        self.ops = ('+', '-', '*', '/', '&', '|', '<', '>', '=')
        self.unaryOps = ('-', '~')
        self.keywordConstants = ('true', 'false', 'null', 'this')
        self.kindKeyword = ''
        self.subroutineKeyword = ''
        self.previousKeyword = ''
        self.lastlastKeyword = ''
        self.lastToken = ''
        self.token_after_kind = ''
        self.lastTokenType = ''
        self.symbol_table = symbol_table
        self.arg_list = False
        self.id_list = False
        self.className = ''
        self.lastlastToken = ''
    def useToken(self):
        while (self.tokenlist[self.token_number][0] == 'NEWLINE') or (self.tokenlist[self.token_number][0] == 'SKIP'):
            self.token_number += 1
            print "skip!"
        token = self.tokenlist[self.token_number][1]
        self.lastTokenType = self.tokenlist[self.token_number][0]
        if (self.lastToken == 'static') or (self.lastToken == 'field') or (self.lastToken == 'var'):
            self.token_after_kind = token
        self.lastlastToken = self.lastToken
        self.lastToken = token
        print token, self.token_number, len(self.tokenlist)
        self.token_number += 1
        return token
    def indicateToken(self):
        while (self.tokenlist[self.token_number][0] == 'NEWLINE') or (self.tokenlist[self.token_number][0] == 'SKIP'):
            self.token_number += 1
            print "skip!"
        print self.tokenlist[self.token_number][1]
        return self.tokenlist[self.token_number][1]
    def getTokenType(self):
        while (self.tokenlist[self.token_number][0] == 'NEWLINE') or (self.tokenlist[self.token_number][0] == 'SKIP'):
            self.token_number += 1
            print "skip!"
        return self.tokenlist[self.token_number][0]
    def boolToken(self, string):
        print  self.indicateToken()     
        return self.indicateToken() == string
    def compileKeyword(self):
        if self.getTokenType() == 'KEYWORD':
            self.lastlastKeyword = self.previousKeyword            
            self.previousKeyword = self.indicateToken()
            if (self.indicateToken() == 'static') or (self.indicateToken() == 'field') or (self.indicateToken() == 'var'):
                self.kindKeyword = self.indicateToken()
            if (self.indicateToken() == 'constructor') or (self.indicateToken() == 'method') or (self.indicateToken() == 'function'):
                self.subroutineKeyword = self.indicateToken()
            return '<keyword> ' + self.useToken() + ''' </keyword>
            '''
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileIdentifier(self):
        if self.getTokenType() == 'IDENTIFIER':
            if self.symbol_table.kindOf(self.indicateToken()) == 'NONE':
                print self.previousKeyword, self.symbol_table.scope, self.symbol_table.name_list, self.symbol_table.name_method_list
                if ((self.lastlastToken == 'static') or (self.lastlastToken == 'field') or (self.lastlastToken == 'var')):
                    condition = '<defined>'
                    kind = self.kindKeyword
                    self.symbol_table.define(self.indicateToken(), self.lastToken, kind)
                    index = self.symbol_table.indexOf(self.indicateToken())
                    print "yay"
                elif self.arg_list == True:
                    condition = '<defined>'
                    kind = 'argument'
                    self.symbol_table.define(self.indicateToken(), self.lastToken, 'arg')
                    index = self.symbol_table.indexOf(self.indicateToken())
                elif self.id_list == True:
                    condition = '<defined>'
                    kind = self.kindKeyword
                    print "t"
                    self.symbol_table.define(self.indicateToken(), self.token_after_kind, kind)
                    print "wh"
                    index = self.symbol_table.indexOf(self.indicateToken())
                    print "techno music"
                else:
                    if self.previousKeyword == 'class':
                        kind = 'class'
                        condition = '<defined>'
                    elif self.tokenlist[self.token_number + 1][1] == ".":
                        kind = 'class'
                        condition = '<used>'
                    elif self.lastToken == self.previousKeyword:
                        kind = 'class'
                        condition = '<used>'
                    elif self.lastTokenType == 'IDENTIFIER':
                        kind = 'subroutine'
                        condition = '<defined>'
                    elif (self.lastToken == 'void') or (self.lastToken == 'int') or (self.lastToken == 'char') or (self.lastToken == 'boolean'):
                        kind = 'subroutine'
                        condition = '<defined>'
                    elif self.previousKeyword == 'do':
                        kind = 'subroutine'
                        condition = '<used>'
                    elif self.lastToken == '.':
                        kind = 'subroutine'
                        condition = '<used>'
                    index = 'none'
            else:
                condition = '<used>'
                kind = self.symbol_table.kindOf(self.indicateToken())
                index = self.symbol_table.indexOf(self.indicateToken())
            print '<identifier>'+ condition +'<'+ kind + '><'+ str(index) + '> ' + self.indicateToken() + ''' </identifier>
            '''
            return '<identifier>'+ condition +'<'+ kind + '><'+ str(index) + '> ' + self.useToken() + ''' </identifier>
            '''
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileSymbol(self):
        if self.getTokenType() == 'SYMBOL':
            return '<symbol> ' + self.useToken() + ''' </symbol>
            '''
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileIntegerConstant(self):
        if self.getTokenType() == 'INT_CONST':
            return '<integerConstant> ' + self.useToken() + ''' </integerConstant>
            '''
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileStringConstant(self):
        if self.getTokenType() == 'STRING_CONST':
            return '<stringConstant> ' + self.useToken() + ''' </stringConstant>
            '''
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileType(self):
        if self.getTokenType() == 'IDENTIFIER':
            return self.compileIdentifier()
        elif (self.indicateToken() == 'int') or (self.indicateToken() == 'char') or (self.indicateToken() == 'boolean'):
            return self.compileKeyword()
        else:
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
    def compileClass(self):
        self.className = self.indicateToken()
        xmlstr = '''<class>
        '''
        print 1
        xmlstr += self.compileKeyword()
        print 2
        xmlstr += self.compileIdentifier()
        print 3
        xmlstr += self.compileSymbol()
        print self.token_number
        while self.indicateToken() != '}':
            print "I know you're endless looping!!! ", self.getTokenType()
            if (self.boolToken('constructor')) or (self.boolToken('function')) or (self.boolToken('method')):
                xmlstr += self.compileSubroutine()
            elif (self.boolToken('field')) or (self.boolToken('static')):
                xmlstr += self.compileClassVarDec()
            else:
                print 1 % 0
        xmlstr += self.compileSymbol() + '''</class>
        '''
        return xmlstr
    def compileClassVarDec(self):
        xmlstr = '''<classVarDec>
        ''' + self.compileKeyword() + self.compileType() + self.compileIdentifier()
        self.id_list = True
        while self.indicateToken() != ';':
            print "Cuckoo!"
            xmlstr += self.compileSymbol() + self.compileIdentifier()
        if self.indicateToken() != ';':
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
        self.id_list = False
        xmlstr += self.compileSymbol() + '''</classVarDec>
        '''
        return xmlstr
    def compileSubroutine(self):
        xmlstr = '''<subroutineDec>
        ''' + self.compileKeyword()
        self.symbol_table.startSubroutine()
        if self.indicateToken() == 'void':
            xmlstr += self.compileKeyword()
        else:
            xmlstr += self.compileType()
        xmlstr += self.compileIdentifier() 
        self.symbol_table.switchScope()
        xmlstr += self.compileSymbol()
        self.arg_list = True
        self.symbol_table.define('this', self.className, 'arg')
        xmlstr += self.compileParameterList() + self.compileSymbol()
        self.arg_list = False
        xmlstr += self.compileSubroutineBody()
        self.symbol_table.switchScope()
        xmlstr += '''</subroutineDec>
        '''
        print self.tokenlist[self.token_number-1][1]
        return xmlstr
    def compileSubroutineBody(self):
        xmlstr = '''<subroutineBody>
        ''' + self.compileSymbol()
        while (self.indicateToken() == 'static') or (self.indicateToken() == 'field'):
            xmlstr += self.compileVarDec()
        xmlstr += self.compileStatements() + self.compileSymbol()
        xmlstr += '''</subroutineBody>
        '''
        return xmlstr
    def compileParameterList(self):
        xmlstr = '''<parameterList>
        '''
        if self.indicateToken() != ')':
            xmlstr += self.compileType() + self.compileIdentifier()
        while self.indicateToken() != ')':
            print "Woohoo!"
            xmlstr += self.compileSymbol() + self.compileType() + self.compileIdentifier()
        xmlstr += '''</parameterList>
        '''
        return xmlstr
    def compileVarDec(self):
        xmlstr = '''<varDec>
        ''' + self.compileKeyword() + self.compileType() + self.compileIdentifier()
        while self.indicateToken() != ';':
            print "Doops?"
            xmlstr += self.compileSymbol() + self.compileIdentifier()
        if self.indicateToken() != ';':
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
        xmlstr += self.compileSymbol()
        xmlstr += '''</varDec>
        '''
        return xmlstr
    def compileStatements(self):
        xmlstr = '''<statements>
        '''
        while self.indicateToken() == 'var':
            xmlstr = self.compileVarDec()
        while self.indicateToken() != '}':
            print self.token_number, self.indicateToken(), 'TEST3'
            if self.indicateToken() == 'let':
                xmlstr += self.compileLet()
            elif self.indicateToken() == 'if':
                print ''' THIS
                SHOULD
                BE
                OBVIOUS
                '''
                xmlstr += self.compileIf()
            elif self.indicateToken() == 'while':
                xmlstr += self.compileWhile()
            elif self.indicateToken() == 'do':
                xmlstr += self.compileDo()
            elif self.indicateToken() == 'return':
                xmlstr += self.compileReturn()
            else:
                print 5 / 0
        xmlstr += '''</statements>
        '''
        return xmlstr
    def compileDo(self):
        xmlstr = '''<doStatement>
        ''' + self.compileKeyword() + self.compileTerm()
        if self.indicateToken() != ';':
            raise RuntimeError("Unexpected token %r" %self.indicateToken())        
        xmlstr += self.compileSymbol() + '''</doStatement>
        '''
        return xmlstr
    def compileLet(self):
        xmlstr = '''<letStatement>
        ''' + self.compileKeyword() + self.compileIdentifier()
        print self.indicateToken()
        if self.indicateToken() != '=':
            xmlstr += self.compileSymbol() + self.compileExpression() + self.compileSymbol()
        xmlstr += self.compileSymbol() + self.compileExpression()
        if self.indicateToken() != ';':
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
        xmlstr += self.compileSymbol() + '''</letStatement>
        '''
        return xmlstr
    def compileWhile(self):
        xmlstr = '''<whileStatement>
        ''' + self.compileKeyword() + self.compileSymbol() + self.compileExpression() + self.compileSymbol() + self.compileSymbol() + self.compileStatements() + self.compileSymbol() + '''</whileStatement>
        '''
        return xmlstr
    def compileReturn(self):
        xmlstr = '''<returnStatement>
        ''' + self.compileKeyword()
        if self.indicateToken() != ';':
            xmlstr += self.compileExpression()
        if self.indicateToken() != ';':
            raise RuntimeError("Unexpected token %r" %self.indicateToken())
        xmlstr += self.compileSymbol() + '''</returnStatement>
        '''
        return xmlstr
    def compileIf(self):
        xmlstr = '''<ifStatement>
        ''' + self.compileKeyword() + self.compileSymbol() + self.compileExpression() + self.compileSymbol() + self.compileSymbol() + self.compileStatements() + self.compileSymbol()
        if self.indicateToken() == 'else':
            xmlstr += '''<whileStatement>
        ''' + self.compileKeyword() + self.compileExpression() + self.compileSymbol() + self.compileSymbol() + self.compileStatements() + self.compileSymbol()
        print self.indicateToken(), "WKTJKJTHKEHTJKRHKDNFKMNMCMN"
        xmlstr += '''</ifStatement>
        '''
        return xmlstr
    def compileExpression(self):
        xmlstr = '''<expression>
        ''' + self.compileTerm()
        while self.indicateToken() in self.ops:
            print "o_0"
            xmlstr += self.compileSymbol() + self.compileTerm()
        xmlstr += '''</expression>
        '''
        return xmlstr
    def compileTerm(self):
        xmlstr = '''<term>
        '''
        print self.getTokenType()
        print type(self.getTokenType())
        if self.getTokenType() == 'INT_CONST':
            xmlstr += self.compileIntegerConstant()
        elif self.getTokenType() == 'STRING_CONST':
            xmlstr += self.compileStringConstant()
        elif self.getTokenType() == 'KEYWORD':
            print "THIS SHOULD BE OBVIOUS"
            xmlstr += self.compileKeyword()
        elif self.getTokenType() == 'IDENTIFIER':
            xmlstr += self.compileIdentifier()
            if self.indicateToken() == '[':
                xmlstr += self.compileSymbol() + self.compileExpression() + self.compileSymbol()
            elif self.indicateToken() == '(':
                xmlstr += self.compileSymbol() + self.compileExpressionList() + self.compileSymbol()
            elif self.indicateToken() == '.':
                xmlstr += self.compileSymbol() + self.compileIdentifier() + self.compileSymbol() + self.compileExpressionList() + self.compileSymbol()
        elif self.indicateToken() == '(':
            xmlstr += self.compileSymbol() + self.compileExpression() + self.compileSymbol()
        elif (self.indicateToken() == '-') or (self.indicateToken() == '~'):
            xmlstr += self.compileSymbol() + self.compileTerm()
        xmlstr += '''</term>
        '''
        return xmlstr
    def compileExpressionList(self):
        xmlstr = '''<expressionList>
        '''
        if self.indicateToken() != ')':
            xmlstr += self.compileExpression()
        while self.indicateToken() != ')':
            print ["l", "i", "s", "t"]
            xmlstr += self.compileSymbol() + self.compileExpression()
        xmlstr += '''</expressionList>
        '''
        return xmlstr
        
class SymbolTable:
    def __init__(self):
        self.name_list = []
        self.type_list = []
        self.kind_list = []
        self.index_list = []
        self.name_method_list = []
        self.type_method_list = []
        self.kind_method_list = []
        self.index_method_list = []
        self.static_index = 0
        self.field_index = 0
        self.argument_index = 0
        self.var_index = 0
        self.scope = False # false for class-scope, true for method scope
    def startSubroutine(self):
        self.name_method_list = []
        self.type_method_list = []
        self.kind_method_list = []
        self.index_method_list = []
        self.argument_index = 0
        self.var_index = 0
    def switchScope(self):
        self.scope = not(self.scope)
    def define(self, name, type, kind):
        if (kind == "static") or (kind == "field"):
            self.name_list.append(name)
            self.type_list.append(type)
            self.kind_list.append(kind)
            if type == "static":
                number = self.static_index
                self.static_index += 1
            else:
                number = self.field_index
                self.field_index += 1
            self.index_list.append(number)
        elif (kind == "arg") or (kind == "var"):
            self.name_method_list.append(name)
            self.type_method_list.append(type)
            self.kind_method_list.append(kind)
            if type == "arg":
                number = self.argument_index
                self.argument_index += 1
            else:
                number = self.var_index
                self.var_index += 1
            self.index_method_list.append(number)
        else:
            raise RuntimeError("Invalid type: %r" %(type))
    def varCount(self, kind):
        if kind == "static":
            return self.static_index
        if kind == "field":
            return self.field_index
        if kind == "arg":
            return self.argument_index
        if kind == "var":
            return self.var_index
        else:
            raise RuntimeError("Invalid type: %r" %(type))
    def kindOf(self, name):
        some_number = -1
        if self.scope == True:
            i = 0
            while i < len(self.name_method_list):
                if name == self.name_method_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                pass
            else:
                return self.kind_method_list[some_number]
        if True:
            i = 0
            while i < len(self.name_list):
                if name == self.name_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                return "NONE"
            else:
                return self.kind_list[some_number]
    def typeOf(self, name):
        some_number = -1
        if self.scope == True:
            i = 0
            while i < len(self.name_method_list):
                if name == self.name_method_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                pass
            else:
                return self.type_method_list[some_number]
        if True:
            i = 0
            while i < len(self.name_list):
                if name == self.name_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                return ""
            else:
                return self.type_list[some_number]
    def indexOf(self, name):
        some_number = -1
        if self.scope == True:
            i = 0
            while i < len(self.name_method_list):
                if name == self.name_method_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                pass
            else:
                return self.index_method_list[some_number]
        if True:
            i = 0
            while i < len(self.name_list):
                if name == self.name_list[i]:
                    some_number = i
                i += 1
            if some_number == -1:
                return "NONE"
            else:
                return self.index_list[some_number]

def tokenize(file, outputfile):
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
    outfile = open(outputfile, "w+")
    symbol_table = SymbolTable()
    compilation = CompilationEngine(tokenizer.tokens, outfile, symbol_table)
    print compilation.compileClass()
    #outfile.write(compilation.compileClass())
    outfile.close()
    
    
print "Hello! We are sdalfkjsdlfsad"    
tokenize("Square.jack", "Square.xml")
#tokenize("SquareGame.jack", "SquareGame.xml")
#tokenize("Main.jack", "Main_generated.xml") 

