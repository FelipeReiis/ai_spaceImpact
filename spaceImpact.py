import pygame as pg
import random
import neat 
import os

LARGURA_JANELA = 400  # Definindo a largura fixa
ALTURA_NAVE = 50
ALTURA_JANELA = ALTURA_NAVE * 10  # A tela tem duas vezes o tamanho da nave
geracao = 0

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
    def __init__(self, imagens_aliens, posicao_nave_y):  # Apenas Y da nave é passado
        self.imgAlien = pg.image.load(random.choice(imagens_aliens)).convert_alpha()
        self.imgAlien = pg.transform.scale(self.imgAlien, (50, 50))
        self.areaAlien = self.imgAlien.get_rect()
        self.pos_alien_x = LARGURA_JANELA + 50  # Começa fora da tela (à direita)
        self.pos_alien_y = posicao_nave_y  # A posição Y será a mesma da nave
        self.velocidade = 5.0  # Ajuste a velocidade conforme necessário
        self.tempo_atualizacao = 0
        self.tempo_atualizacao_max = 150

    def colocarAlienNaTela(self, item):
        # Atualiza a hitbox do alien conforme sua posição
        self.areaAlien.topleft = (self.pos_alien_x, self.pos_alien_y)
        # Desenha a hitbox do alien para visualização
        pg.draw.rect(item, (27, 192, 192), self.areaAlien, 4)  
        item.blit(self.imgAlien, (self.pos_alien_x, self.pos_alien_y))

    def movimentarAlien(self):
        self.pos_alien_x -= self.velocidade
        # Código para aumentar a velocidade com o tempo
        self.tempo_atualizacao += 1
        if self.tempo_atualizacao >= self.tempo_atualizacao_max:
            self.velocidade += 4  # Ajuste conforme necessário
            self.tempo_atualizacao = 0
        return self.pos_alien_x



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
        self.velocidade = 5.0
        self.pontuacao = 1
        self.aliens = []
    
    def movimentarParaCima(self):
        if self.pos_nave_y > 10:
            self.pos_nave_y -= self.velocidade

    def movimentarParaBaixo(self):
        if self.pos_nave_y < ALTURA_JANELA - self.areaNave.height:
            self.pos_nave_y += self.velocidade
    
    def criarAliens(self, imagens_aliens):
        novo_alien = Alien(imagens_aliens, self.pos_nave_y)  # Passa apenas a posição Y da nave
        self.aliens.append(novo_alien)

    
    def colocarAliensNaTela(self, item):
        for alien in self.aliens[:]:  # Usando uma cópia da lista para evitar modificação durante a iteração
            alien.colocarAlienNaTela(item)
            alien.movimentarAlien()
            if alien.pos_alien_x < -alien.areaAlien.width:  # Se o alien sair da tela
                self.aliens.remove(alien)  # Remover da lista

    def colocarNaveNaTela(self, item):
        # Atualiza a hitbox da nave conforme sua posição
        self.areaNave.topleft = (self.pos_nave_x, self.pos_nave_y)
        # Desenha a hitbox da nave para visualização
        pg.draw.rect(item, (0, 255, 0), self.areaNave, 2)  
        item.blit(self.imgNave, (self.pos_nave_x, self.pos_nave_y))

    def obterPontuacao(self):
        return self.pontuacao

    def colisaoNaveAlien(nave, alien):
        return nave.areaNave.colliderect(alien.areaAlien)

# Função principal que aplica a IA com NEAT
def spaceImpact(genomas, config):
    global geracao
    geracao += 1
    pg.init()

    ALTURA_NAVE = 50
    LARGURA_NAVE = 50
    ALTURA_JANELA = ALTURA_NAVE * 10
    LARGURA_JANELA = 400

    tela = pg.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pg.display.set_caption('Space Impact')

    redes = []
    lista_genomas = []
    naves = []

    for _, genoma in genomas:
        rede = neat.nn.FeedForwardNetwork.create(genoma, config)
        redes.append(rede)
        genoma.fitness = 0
        lista_genomas.append(genoma)
        nave = Nave()
        nave.ultima_posicao_y = nave.pos_nave_y
        nave.tempo_parado = 0
        nave.tempo_movel = 0  # Tempo que a nave está se movendo
        naves.append(nave)

    imagens_aliens = ['imgs/alien_1_1.png', 'imgs/alien_1_2.png']
    plano_fundo = pg.image.load('imgs/background_1.png').convert_alpha()
    clock = pg.time.Clock()

    rodando = True
    while rodando and len(naves) > 0:
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                rodando = False
                pg.quit()
                quit()

        tela.blit(plano_fundo, (0, 0))

        if all(len(nave.aliens) == 0 for nave in naves):
            for nave in naves:
                nave.criarAliens(imagens_aliens)

        naves_removidas = []

        for i, nave in enumerate(naves):
            input_data = []
            # Obter o alien mais próximo e seus dados
            if len(nave.aliens) > 0:
                alien_mais_proximo = nave.aliens[0]  # Como há apenas um alien por vez
                input_data.append(alien_mais_proximo.pos_alien_x - nave.pos_nave_x)  # Distância X
                # input_data.append(alien_mais_proximo.pos_alien_y - nave.pos_nave_y)  # Distância Y
                input_data.append(alien_mais_proximo.velocidade)  # Velocidade do alien
                # input_data.append(ALTURA_NAVE) # tamanho do alien
            else:
                input_data += [0, 0, 0]  # Se não houver aliens, entradas são 0

            input_data.append(nave.pos_nave_y)  # Posição Y da nave

            # Obter a saída da rede neural
            output = redes[i].activate(input_data)

            # Ações da nave - inverter a lógica para verificar
            if output[1] > output[0]:  # Move para cima
                nave.movimentarParaCima()
            elif output[0] > output[1]:  # Move para baixo
                nave.movimentarParaBaixo()

            # teclas = pg.key.get_pressed()
            # if teclas[pg.K_UP]:  # Pressionando a tecla para cima
            #     nave.movimentarParaCima()
            # if teclas[pg.K_DOWN]:  # Pressionando a tecla para baixo
            #     nave.movimentarParaBaixo()

            # Verificar se a nave se moveu no eixo Y
            if nave.pos_nave_y == nave.ultima_posicao_y:
                nave.tempo_parado += 1  # Incrementa o tempo que a nave está parada
            else:
                nave.tempo_parado = 0  # Reseta o tempo parado se a nave se mover

            # Aumentar fitness quando desviar de alien com sucesso
            if alien_mais_proximo.pos_alien_x < nave.pos_nave_x and not colisaoNaveAlien(nave.areaNave, alien_mais_proximo.areaAlien):
                lista_genomas[i].fitness += 2  # Recompensa por desvio bem-sucedido

            # Punir se a nave estiver parada por mais de 1 segundo (60 frames)
            if nave.tempo_parado > 60:  # 60 frames = 1 segundo
                lista_genomas[i].fitness -= 0.5  # Penaliza levemente a fitness
                nave.tempo_parado = 0  # Reseta o tempo parado após penalização

            nave.ultima_posicao_y = nave.pos_nave_y  # Atualiza a última posição Y

            nave.colocarNaveNaTela(tela)
            nave.colocarAliensNaTela(tela)

            # Atualizar a posição dos aliens para seguir as naves
            for alien in nave.aliens:
                alien.movimentarAlien()

                hit_box_nave = nave.areaNave.move(nave.pos_nave_x, nave.pos_nave_y)
                hit_box_alien = alien.areaAlien.move(alien.pos_alien_x, alien.pos_alien_y)

                if colisaoNaveAlien(hit_box_nave, hit_box_alien):
                    lista_genomas[i].fitness -= 4
                    naves_removidas.append(nave)
                    break

        for nave_removida in naves_removidas:
            naves.remove(nave_removida)

        pg.display.update()
        clock.tick(60)

    pg.quit()


# Função principal para rodar o NEAT
def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                          neat.DefaultStagnation, config_file)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    estatisticas = neat.StatisticsReporter()
    p.add_reporter(estatisticas)
    # Definir o número de gerações para evoluir
    p.run(spaceImpact, 100)

# Chamada da função principal
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config_Ia_space_impact.txt')
    run(config_path)
