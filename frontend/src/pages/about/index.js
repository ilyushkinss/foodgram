import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Foodgram - это сайт, позволяющий пользователям создавать и делиться своими рецептами, подписываться на других людей, и много чего еще. В общем, как маленькая социальная сеть для любителей кулинарии!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта - <a href="https://github.com/ilyushkinss/foodgram" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: Гильманов Илья
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

