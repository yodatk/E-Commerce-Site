import React, {Component} from "react";
import {MDBBadge, MDBBtn, MDBContainer, MDBLink, MDBTable, MDBTableBody, MDBTableHead} from "mdbreact";
import axios from "axios";
import {Button} from "semantic-ui-react";

export class MyStores extends Component {
    state = {
        stores: []
    }

    componentDidMount() {
        axios.get(
            "/fetch_stores/" + this.props.getUserId())
            .then((res) => {
                this.setState({stores: res.data !== null && 'stores' in res.data ? res.data.stores : []})
            }).catch(error => {
            console.log(error)
        });
    }

    render() {
        return (
            <MDBContainer>
                <MDBTable>
                    <MDBTableHead color="primary-color" textWhite>
                        <tr>
                            <th>#</th>
                            <th>Store name</th>
                            <th>Initial owner</th>
                            <th>Status</th>
                            <th>Creation Date</th>
                            <th>Manage</th>
                        </tr>
                    </MDBTableHead>
                    <MDBTableBody>
                        {this.state.stores.map((store, i) => (
                            <tr key={i}>
                                <td>{i + 1}</td>
                                <td>{store.name}</td>
                                <td>{store.initial_owner}</td>
                                <td>{store.open ? 'open' : 'closed'}</td>
                                <td>{store.creation_date}</td>
                                <td><MDBLink key={store.name + "_" + i}
                                             to={"/store_page/" + store.name}><MDBBtn>Manage</MDBBtn></MDBLink></td>
                            </tr>
                        ))}
                    </MDBTableBody>
                </MDBTable>


            </MDBContainer>
        );
    }
}

export default MyStores;