import pygame as pg
import random
import neat 

LARGURA_JANELA = 500
ALTURA_JANELA = 500
class Vida():
    def __init__(self, imagem_vida, posicao):
        self.imagemVida = pg.image.load('imgs/heart.png').convert_alpha()
        self.imagemVida = pg.transform.scale(self.imagemVida, (30, 30))
        self.areaVida = self.imagemVida.get_rect()
        self.areaVida.topleft = posicao
        self.vida = 3  # Adicione um contador de vidas
        self.invulneravel = False  # Adicione um indicador de invulnerabilidade
        self.tempo_invulneravel = 120  # Defina o tempo de invulnerabilidade em iterações (60 iterações por segundo)

    def perderVida(self):
        if not self.invulneravel:  # Verifica se a nave não está invulnerável
            self.vida -= 1
            self.invulneravel = True    

    def colocarVidaNaTela(self, item):
        item.blit(self.imagemVida, self.areaVida.topleft)
    
    def colidir(self):
        self.colidida = True

    def naoColidir(self):
        self.colidida = False

def colisao(projetil, alien):
    return projetil.colliderect(alien)

def colisaoNaveAlien(nave, alien):
    return nave.colliderect(alien)

class Alien():
    def __init__(self, imagens_aliens):
        self.imgAlien = pg.image.load(random.choice(imagens_aliens)).convert_alpha()
        self.imgAlien = pg.transform.scale(self.imgAlien, (50, 50))
        self.areaAlien = self.imgAlien.get_rect()
        self.pos_alien_x = LARGURA_JANELA  # Posição inicial fora da tela
        self.pos_alien_y = random.randint(10, 450)
        self.velocidade = 5.0  # Ajuste a velocidade conforme necessário
        self.tempo_atualizacao = 0
        self.tempo_atualizacao_max = 150
        self.nave = Nave()

    def colocarAlienNaTela(self, item):
        hit_box_alien = self.areaAlien
        hit_box_alien.y = self.pos_alien_y
        hit_box_alien.x = self.pos_alien_x
        pg.draw.rect(item, (27, 192, 192), hit_box_alien, 4)
        item.blit(self.imgAlien, (self.pos_alien_x, self.pos_alien_y))

    def movimentarAlien(self):
        self.pos_alien_x -= self.velocidade

        # Atualizar o contador de tempo
        self.tempo_atualizacao += 1
        if self.tempo_atualizacao >= self.tempo_atualizacao_max:
            # Aumentar a velocidade e reiniciar o contador de tempo
            self.velocidade += 4  # Ajuste conforme necessário
            self.tempo_atualizacao = 0
        return  self.pos_alien_x
class Bala():
    def __init__(self, x, y):
        self.imgProjetil = pg.image.load('imgs/d.png').convert_alpha()
        self.imgProjetil = pg.transform.scale(self.imgProjetil, (8, 8))
        self.areaProjetil = self.imgProjetil.get_rect()
        self.pos_projetil_x = x
        self.pos_projetil_y = y
        self.velocidade = 5.0  # Ajuste a velocidade conforme necessário

    def trajetoria(self):
        self.pos_projetil_x += self.velocidade

    def colocarProjetilNaTela(self, item):
        hit_box_projetil = self.areaProjetil
        hit_box_projetil.y = self.pos_projetil_y
        hit_box_projetil.x = self.pos_projetil_x
        pg.draw.rect(item, (56, 66, 55), hit_box_projetil, 4)
        item.blit(self.imgProjetil, (self.pos_projetil_x, self.pos_projetil_y))

def colisao(projetil, alien):
    return projetil.colliderect(alien)

class Nave():
    def __init__(self):
        self.imgNave = pg.image.load('imgs/ship_1.png').convert_alpha()
        self.imgNave = pg.transform.scale(self.imgNave, (50, 50))
        self.areaNave = self.imgNave.get_rect()
        self.pos_nave_x = 50
        self.pos_nave_y = 250
        self.aliens = []
        self.disparos = []
        self.vida = True
        self.velocidade = 5.0  # Ajuste a velocidade conforme necessário
        self.invulneravel = False  # Adicione o atributo invulneravel
        self.tempo_invulneravel = 0  # Adicione o atributo tempo_invulneravel
        self.pontuacao = 1

    def disparar(self):
        x, y = self.pos_nave_x + self.areaNave.width, self.pos_nave_y + self.areaNave.height // 2
        bala = Bala(x, y)
        self.disparos.append(bala)

    def movimentarParaCima(self):
        if self.pos_nave_y > 10:
            self.pos_nave_y -= self.velocidade

    def movimentarParaDireita(self):
        if self.pos_nave_x < LARGURA_JANELA - self.areaNave.width:
            self.pos_nave_x += self.velocidade

    def movimentarParaBaixo(self):
        if self.pos_nave_y < ALTURA_JANELA - self.areaNave.height:
            self.pos_nave_y += self.velocidade

    def movimentarParaEsquerda(self):
        if self.pos_nave_x > 1:
            self.pos_nave_x -= self.velocidade

    def colocarNaveNaTela(self, item):
        hit_box_nave = self.areaNave
        hit_box_nave.y = self.pos_nave_y
        hit_box_nave.x = self.pos_nave_x
        pg.draw.rect(item, (27, 192, 192), hit_box_nave, 4)
        item.blit(self.imgNave, (self.pos_nave_x, self.pos_nave_y))

    def criarAliens(self, imagens_aliens):
        novo_alien = Alien(imagens_aliens)
        self.aliens.append(novo_alien)

    def colocarAliensNaTela(self, item):
        for alien in self.aliens:
            alien.colocarAlienNaTela(item)
            alien.movimentarAlien()
            print(alien.movimentarAlien())
            if alien.movimentarAlien() == self.pos_nave_x:
                self.pontuacao+=0.5
    def verificarColisoes(self, vidas, imagens_aliens):
        disparos_para_remover = []
        aliens_para_remover = []
        novos_aliens = []  # Lista para armazenar novos aliens

        for disparo in self.disparos:
            for alien in self.aliens:
                if colisao(disparo.areaProjetil, alien.areaAlien):
                    disparos_para_remover.append(disparo)
                    aliens_para_remover.append(alien)
                    self.pontuacao += 10
                    
                    
        for disparo in disparos_para_remover:
            if disparo in self.disparos:
                self.disparos.remove(disparo)

        for alien in aliens_para_remover:
            if alien in self.aliens:
                # Adicionar alien à lista de novos aliens
                novos_aliens.append(Alien(imagens_aliens))
                self.aliens.remove(alien)


        # Adicionar novos aliens à lista de aliens
        self.aliens.extend(novos_aliens)

        # Verificar colisão entre a nave e os aliens
        for alien in self.aliens:
            if colisaoNaveAlien(self.areaNave, alien.areaAlien):
                if not self.invulneravel:
                    # Reposicionar a nave após a colisão
                    self.reposicionarNave()
                    self.invulneravel = True
                    self.pontuacao -= 2
                    # Remover uma vida se houver colisão
                    if vidas:
                        vidas.pop()
                        self.invulneravel = False

    def reposicionarNave(self):
        self.pos_nave_x = 50
        self.pos_nave_y = 250

    def obterPontuacao(self):
        return self.pontuacao
geracao = 0
def spaceImpact(genomas, config):
    redes = []
    lista_genomas = []
    naves = []
    global geracao 
    geracao+=1
   

    pg.init()
    LARGURA_JANELA = 500
    ALTURA_JANELA = 500
    tela = pg.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pg.display.set_caption('Space Impact')
    jogador = Nave()
    # alien = Alien()
    for _, genoma in genomas:
        rede = neat.FeedForwardNetwork.create(genoma, config)
        redes.append(rede)
        genoma.fitness = 0
        lista_genomas.append(genoma)        
        naves.append(jogador.colocarNaveNaTela(tela))
    plano_fundo = pg.image.load('imgs/background_1.png').convert_alpha()

    imagens_aliens = ['imgs/alien_1_1.png', 'imgs/alien_1_2.png', 'imgs/alien_2_1.png', 'imgs/alien_2_2.png', 'imgs/alien_3_1.png', 'imgs/alien_3_2.png']
    imagem_vida = 'caminho/para/imagem_de_vida.png'  # Substitua pelo caminho real da sua imagem de vida

    vidas = [Vida(imagem_vida, (LARGURA_JANELA - i * 40, 10)) for i in range(1,4)]  # Posiciona as vidas no canto superior direito

    colisao_ativa = False  # Variável de controle para evitar remoção múltipla de vidas

    clock = pg.time.Clock()

    while True:
        if len(vidas) == 0:
            pg.quit()
            quit()
        tecla = pg.key.get_pressed()
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                quit()
        tela.blit(plano_fundo, (0, 0))
        resto_tela = LARGURA_JANELA % plano_fundo.get_rect().width
        tela.blit(plano_fundo,(resto_tela - plano_fundo.get_rect().width,0))
        if resto_tela < 500:
            tela.blit(plano_fundo,(resto_tela, 0))  
        # Reiniciar variável de controle a cada iteração do loop
        colisao_ativa = False

        jogador.movimentarParaCima() if tecla[pg.K_UP] else None
        jogador.movimentarParaDireita() if tecla[pg.K_RIGHT] else None
        jogador.movimentarParaBaixo() if tecla[pg.K_DOWN] else None
        jogador.movimentarParaEsquerda() if tecla[pg.K_LEFT] else None
        jogador.disparar() if tecla[pg.K_SPACE] else None

        # Criar novos aliens aleatoriamente
        if random.randint(0, 100) < 2:
            jogador.criarAliens(imagens_aliens)

        # Mover e exibir todos os aliens        
        jogador.colocarAliensNaTela(tela)
        # print(alien.pos_alien_x)
        if len(jogador.disparos) > 0:
            for disparo in jogador.disparos:
                disparo.trajetoria()
                if len(jogador.disparos) <= 5:
                     disparo.colocarProjetilNaTela(tela)                
                else:
                     jogador.disparos.clear()

        LARGURA_JANELA -=1


        # jogador.colocarNaveNaTela(tela)

        # Verificar colisões
        jogador.verificarColisoes(vidas,imagens_aliens)

        # Exibir as vidas
        for vida in vidas:
            vida.colocarVidaNaTela(tela)

        fonte = pg.font.Font(None, 36)
        pontuacao_texto = fonte.render(f'Pontuação: {jogador.obterPontuacao()}', True, (255, 255, 255))
        geracao_texto = fonte.render(f'Geração: {geracao}', True, (255, 255, 255))
        tela.blit(pontuacao_texto, (10, 10))
        tela.blit(geracao_texto, (200, 10))
        # Atualizar a tela e controlar o FPS
        pg.display.update()
        clock.tick(60)

spaceImpact()
